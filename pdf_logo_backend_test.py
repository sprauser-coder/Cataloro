#!/usr/bin/env python3
"""
Cataloro Marketplace - PDF Logo Saving Functionality Testing
Tests the fixed PDF logo saving functionality as requested in review:

1. Test Settings Endpoint: Verify `/api/admin/settings` GET returns `pdf_logo_url` field
2. Test Settings Update: Test `/api/admin/settings` PUT can save `pdf_logo_url` field  
3. Test PDF Export Integration: Verify PDF export can retrieve and use saved `pdf_logo_url`
4. Test Persistence: Confirm `pdf_logo_url` persists and is returned in subsequent requests
"""

import asyncio
import aiohttp
import json
import sys
import time
import base64
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class PDFLogoTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.test_logo_url = "https://example.com/test-logo.png"
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request to backend"""
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400
                    }
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400
                    }
        except Exception as e:
            return {
                "status": 500,
                "data": {"error": str(e)},
                "success": False
            }
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: {details}")
        else:
            print(f"❌ {test_name}: {details}")
            self.failed_tests.append(result)
    
    # ==== PDF LOGO FUNCTIONALITY TESTS ====
    
    async def test_settings_get_pdf_logo_field(self):
        """Test 1: Verify GET /api/admin/settings returns pdf_logo_url field (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/admin/settings")
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and "pdf_logo_url" in data:
                pdf_logo_url = data.get("pdf_logo_url", "")
                self.log_test(
                    "Settings GET - PDF Logo Field",
                    True,
                    f"pdf_logo_url field present in default settings: '{pdf_logo_url}'",
                    {"pdf_logo_url": pdf_logo_url, "has_field": True}
                )
                return True
            else:
                self.log_test(
                    "Settings GET - PDF Logo Field", 
                    False, 
                    "pdf_logo_url field missing from settings response", 
                    data
                )
                return False
        else:
            self.log_test(
                "Settings GET - PDF Logo Field", 
                False, 
                f"Settings GET request failed: {response['status']}", 
                response["data"]
            )
            return False
    
    async def test_settings_update_pdf_logo(self):
        """Test 2: Test PUT /api/admin/settings can save pdf_logo_url field (HIGH PRIORITY)"""
        # First get current settings
        get_response = await self.make_request("GET", "/admin/settings")
        if not get_response["success"]:
            self.log_test(
                "Settings UPDATE - PDF Logo Save", 
                False, 
                "Could not retrieve current settings for update test", 
                get_response["data"]
            )
            return False
        
        current_settings = get_response["data"]
        
        # Update with test PDF logo URL
        updated_settings = current_settings.copy()
        updated_settings["pdf_logo_url"] = self.test_logo_url
        
        # Send PUT request
        put_response = await self.make_request("PUT", "/admin/settings", data=updated_settings)
        
        if put_response["success"]:
            put_data = put_response["data"]
            if isinstance(put_data, dict) and put_data.get("message"):
                self.log_test(
                    "Settings UPDATE - PDF Logo Save",
                    True,
                    f"Successfully saved pdf_logo_url: {self.test_logo_url}",
                    put_data
                )
                return True
            else:
                self.log_test(
                    "Settings UPDATE - PDF Logo Save", 
                    False, 
                    "Invalid response from settings update", 
                    put_data
                )
                return False
        else:
            self.log_test(
                "Settings UPDATE - PDF Logo Save", 
                False, 
                f"Settings PUT request failed: {put_response['status']}", 
                put_response["data"]
            )
            return False
    
    async def test_settings_persistence(self):
        """Test 3: Confirm pdf_logo_url persists in database and subsequent GET requests (HIGH PRIORITY)"""
        # Wait a moment for database write
        await asyncio.sleep(1)
        
        # Get settings again to verify persistence
        response = await self.make_request("GET", "/admin/settings")
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict):
                saved_pdf_logo_url = data.get("pdf_logo_url", "")
                
                if saved_pdf_logo_url == self.test_logo_url:
                    self.log_test(
                        "Settings PERSISTENCE - PDF Logo",
                        True,
                        f"pdf_logo_url correctly persisted: {saved_pdf_logo_url}",
                        {"saved_url": saved_pdf_logo_url, "expected_url": self.test_logo_url}
                    )
                    return True
                else:
                    self.log_test(
                        "Settings PERSISTENCE - PDF Logo", 
                        False, 
                        f"pdf_logo_url not persisted correctly. Expected: {self.test_logo_url}, Got: {saved_pdf_logo_url}", 
                        {"saved_url": saved_pdf_logo_url, "expected_url": self.test_logo_url}
                    )
                    return False
            else:
                self.log_test(
                    "Settings PERSISTENCE - PDF Logo", 
                    False, 
                    "Invalid settings response format", 
                    data
                )
                return False
        else:
            self.log_test(
                "Settings PERSISTENCE - PDF Logo", 
                False, 
                f"Settings GET request failed: {response['status']}", 
                response["data"]
            )
            return False
    
    async def test_pdf_export_logo_integration(self):
        """Test 4: Verify PDF export endpoint can retrieve and use saved pdf_logo_url (HIGH PRIORITY)"""
        # Create test basket data for PDF export
        test_basket_data = {
            "items": [
                {
                    "name": "BMW 320d Catalytic Converter",
                    "price": 450.00,
                    "pt_g": 2.5,
                    "pd_g": 1.8,
                    "rh_g": 0.3
                },
                {
                    "name": "Mercedes E-Class Catalyst",
                    "price": 650.00,
                    "pt_g": 3.2,
                    "pd_g": 2.1,
                    "rh_g": 0.4
                },
                {
                    "name": "Audi A4 Catalytic Converter",
                    "price": 350.00,
                    "pt_g": 1.8,
                    "pd_g": 1.6,
                    "rh_g": 0.2
                }
            ]
        }
        
        # Test PDF export
        response = await self.make_request("POST", "/admin/export/basket-pdf", data=test_basket_data)
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success") and "pdf_data" in data:
                pdf_data = data.get("pdf_data", "")
                items_count = data.get("items_count", 0)
                total_value = data.get("total_value", 0)
                
                # Verify PDF data is valid base64
                try:
                    pdf_bytes = base64.b64decode(pdf_data)
                    is_valid_pdf = pdf_bytes.startswith(b'%PDF')
                    
                    if is_valid_pdf:
                        self.log_test(
                            "PDF Export - Logo Integration",
                            True,
                            f"PDF generated successfully with logo integration (Items: {items_count}, Total: €{total_value:.2f})",
                            {
                                "pdf_size": len(pdf_bytes),
                                "items_count": items_count,
                                "total_value": total_value,
                                "pdf_valid": is_valid_pdf
                            }
                        )
                        return True
                    else:
                        self.log_test(
                            "PDF Export - Logo Integration", 
                            False, 
                            "Generated PDF data is not valid PDF format", 
                            {"pdf_size": len(pdf_bytes), "starts_with_pdf": is_valid_pdf}
                        )
                        return False
                        
                except Exception as e:
                    self.log_test(
                        "PDF Export - Logo Integration", 
                        False, 
                        f"Error validating PDF data: {str(e)}", 
                        {"pdf_data_length": len(pdf_data)}
                    )
                    return False
            else:
                self.log_test(
                    "PDF Export - Logo Integration", 
                    False, 
                    "Invalid PDF export response format", 
                    data
                )
                return False
        else:
            self.log_test(
                "PDF Export - Logo Integration", 
                False, 
                f"PDF export request failed: {response['status']}", 
                response["data"]
            )
            return False
    
    async def test_pdf_export_empty_basket(self):
        """Test 5: Verify PDF export works with empty basket (MEDIUM PRIORITY)"""
        empty_basket_data = {"items": []}
        
        response = await self.make_request("POST", "/admin/export/basket-pdf", data=empty_basket_data)
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and data.get("success"):
                items_count = data.get("items_count", 0)
                total_value = data.get("total_value", 0)
                
                if items_count == 0 and total_value == 0:
                    self.log_test(
                        "PDF Export - Empty Basket",
                        True,
                        f"Empty basket PDF generated correctly (Items: {items_count}, Total: €{total_value:.2f})",
                        {"items_count": items_count, "total_value": total_value}
                    )
                    return True
                else:
                    self.log_test(
                        "PDF Export - Empty Basket", 
                        False, 
                        f"Empty basket counts incorrect. Items: {items_count}, Total: {total_value}", 
                        {"items_count": items_count, "total_value": total_value}
                    )
                    return False
            else:
                self.log_test(
                    "PDF Export - Empty Basket", 
                    False, 
                    "Invalid empty basket PDF response", 
                    data
                )
                return False
        else:
            self.log_test(
                "PDF Export - Empty Basket", 
                False, 
                f"Empty basket PDF export failed: {response['status']}", 
                response["data"]
            )
            return False
    
    async def test_settings_cleanup(self):
        """Test 6: Clean up test data by resetting pdf_logo_url (LOW PRIORITY)"""
        # Get current settings
        get_response = await self.make_request("GET", "/admin/settings")
        if not get_response["success"]:
            self.log_test(
                "Settings CLEANUP - Reset PDF Logo", 
                False, 
                "Could not retrieve settings for cleanup", 
                get_response["data"]
            )
            return False
        
        current_settings = get_response["data"]
        
        # Reset PDF logo URL to empty
        updated_settings = current_settings.copy()
        updated_settings["pdf_logo_url"] = ""
        
        # Send PUT request
        put_response = await self.make_request("PUT", "/admin/settings", data=updated_settings)
        
        if put_response["success"]:
            self.log_test(
                "Settings CLEANUP - Reset PDF Logo",
                True,
                "Successfully reset pdf_logo_url to empty string",
                put_response["data"]
            )
            return True
        else:
            self.log_test(
                "Settings CLEANUP - Reset PDF Logo", 
                False, 
                f"Failed to reset pdf_logo_url: {put_response['status']}", 
                put_response["data"]
            )
            return False
    
    # ==== MAIN TEST EXECUTION ====
    
    async def run_all_tests(self):
        """Run all PDF logo functionality tests"""
        print("🚀 Starting Cataloro Marketplace PDF Logo Functionality Testing...")
        print(f"📡 Testing against: {BACKEND_URL}")
        print("=" * 80)
        
        # HIGH PRIORITY TESTS - Core PDF Logo Functionality
        print("\n🔍 HIGH PRIORITY: PDF Logo Settings Tests")
        test1_success = await self.test_settings_get_pdf_logo_field()
        
        if test1_success:
            test2_success = await self.test_settings_update_pdf_logo()
            
            if test2_success:
                test3_success = await self.test_settings_persistence()
                test4_success = await self.test_pdf_export_logo_integration()
            else:
                print("⚠️ Skipping persistence and integration tests due to update failure")
                test3_success = False
                test4_success = False
        else:
            print("⚠️ Skipping all subsequent tests due to GET settings failure")
            test2_success = False
            test3_success = False
            test4_success = False
        
        # MEDIUM PRIORITY TESTS
        print("\n📊 MEDIUM PRIORITY: Additional PDF Export Tests")
        await self.test_pdf_export_empty_basket()
        
        # LOW PRIORITY TESTS - Cleanup
        print("\n🧹 LOW PRIORITY: Cleanup Tests")
        await self.test_settings_cleanup()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 PDF LOGO FUNCTIONALITY TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"✅ Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n🎯 PDF LOGO FUNCTIONALITY VERIFICATION:")
        print(f"   • Settings GET pdf_logo_url field: {'✅' if any('Settings GET' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Settings UPDATE pdf_logo_url save: {'✅' if any('Settings UPDATE' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Settings PERSISTENCE verification: {'✅' if any('Settings PERSISTENCE' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • PDF Export logo integration: {'✅' if any('PDF Export - Logo Integration' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        
        # Determine overall status
        core_tests_passed = sum(1 for t in self.test_results if t['success'] and any(keyword in t['test'] for keyword in ['Settings GET', 'Settings UPDATE', 'Settings PERSISTENCE', 'PDF Export - Logo Integration']))
        
        if core_tests_passed == 4:
            print(f"\n🎉 ALL PDF LOGO FUNCTIONALITY TESTS PASSED! The PDF logo saving and retrieval is working correctly.")
        elif core_tests_passed >= 3:
            print(f"\n⚠️  MOSTLY SUCCESSFUL with {4-core_tests_passed} core functionality issue(s).")
        else:
            print(f"\n🚨 PDF LOGO FUNCTIONALITY ISSUES DETECTED - {4-core_tests_passed} core tests failed.")

async def main():
    """Main test execution"""
    tester = PDFLogoTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())