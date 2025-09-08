#!/usr/bin/env python3
"""
Cataloro Marketplace - PDF Logo Reset Issue Testing
Comprehensive testing of the fixed PDF logo reset issue as requested in review:

1. Test Settings Cycle: GET current settings, PUT with PDF logo URL, GET again to verify persistence
2. Test PDF Export with Logo: Generate PDF export with saved PDF logo URL, verify no reset occurs
3. Test Settings Persistence After Operations: Multiple GET/PUT operations, verify pdf_logo_url persists through multiple save cycles
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
BACKEND_URL = "https://mega-dashboard.preview.emergentagent.com/api"

class PDFLogoResetTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.test_logo_urls = [
            "https://example.com/logo1.png",
            "https://example.com/logo2.png", 
            "https://example.com/logo3.png"
        ]
        self.original_settings = None
        
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
    
    # ==== COMPREHENSIVE PDF LOGO RESET TESTS ====
    
    async def test_1_settings_cycle_basic(self):
        """Test 1: Basic Settings Cycle - GET current settings to check if pdf_logo_url exists"""
        print("\n🔍 TEST 1: Basic Settings Cycle")
        
        response = await self.make_request("GET", "/admin/settings")
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and "pdf_logo_url" in data:
                pdf_logo_url = data.get("pdf_logo_url", "")
                self.original_settings = data.copy()  # Store original settings
                
                self.log_test(
                    "Settings Cycle - GET Current Settings",
                    True,
                    f"Successfully retrieved settings with pdf_logo_url field: '{pdf_logo_url}'",
                    {"pdf_logo_url": pdf_logo_url, "settings_keys": list(data.keys())}
                )
                return True
            else:
                self.log_test(
                    "Settings Cycle - GET Current Settings", 
                    False, 
                    "pdf_logo_url field missing from settings response", 
                    data
                )
                return False
        else:
            self.log_test(
                "Settings Cycle - GET Current Settings", 
                False, 
                f"Settings GET request failed: {response['status']}", 
                response["data"]
            )
            return False
    
    async def test_2_settings_cycle_put_verify(self):
        """Test 2: PUT settings with test PDF logo URL, then GET again to verify persistence"""
        print("\n🔍 TEST 2: Settings Cycle PUT and Verify")
        
        if not self.original_settings:
            self.log_test(
                "Settings Cycle - PUT and Verify", 
                False, 
                "No original settings available for update test", 
                None
            )
            return False
        
        # Update with first test logo URL
        updated_settings = self.original_settings.copy()
        updated_settings["pdf_logo_url"] = self.test_logo_urls[0]
        
        # PUT request
        put_response = await self.make_request("PUT", "/admin/settings", data=updated_settings)
        
        if not put_response["success"]:
            self.log_test(
                "Settings Cycle - PUT and Verify", 
                False, 
                f"Settings PUT request failed: {put_response['status']}", 
                put_response["data"]
            )
            return False
        
        # Wait for database write
        await asyncio.sleep(1)
        
        # GET again to verify persistence
        get_response = await self.make_request("GET", "/admin/settings")
        
        if get_response["success"]:
            data = get_response["data"]
            if isinstance(data, dict):
                saved_pdf_logo_url = data.get("pdf_logo_url", "")
                
                if saved_pdf_logo_url == self.test_logo_urls[0]:
                    self.log_test(
                        "Settings Cycle - PUT and Verify",
                        True,
                        f"Settings cycle successful: PUT saved and GET retrieved pdf_logo_url: {saved_pdf_logo_url}",
                        {"saved_url": saved_pdf_logo_url, "expected_url": self.test_logo_urls[0]}
                    )
                    return True
                else:
                    self.log_test(
                        "Settings Cycle - PUT and Verify", 
                        False, 
                        f"Settings cycle failed: Expected {self.test_logo_urls[0]}, Got {saved_pdf_logo_url}", 
                        {"saved_url": saved_pdf_logo_url, "expected_url": self.test_logo_urls[0]}
                    )
                    return False
            else:
                self.log_test(
                    "Settings Cycle - PUT and Verify", 
                    False, 
                    "Invalid settings response format after PUT", 
                    data
                )
                return False
        else:
            self.log_test(
                "Settings Cycle - PUT and Verify", 
                False, 
                f"Settings GET after PUT failed: {get_response['status']}", 
                get_response["data"]
            )
            return False
    
    async def test_3_pdf_export_with_logo(self):
        """Test 3: Generate PDF export with saved PDF logo URL, verify no reset occurs"""
        print("\n🔍 TEST 3: PDF Export with Logo Integration")
        
        # Create realistic test basket data
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
                }
            ]
        }
        
        # Generate PDF export
        pdf_response = await self.make_request("POST", "/admin/export/basket-pdf", data=test_basket_data)
        
        if not pdf_response["success"]:
            self.log_test(
                "PDF Export with Logo - Generation", 
                False, 
                f"PDF export request failed: {pdf_response['status']}", 
                pdf_response["data"]
            )
            return False
        
        # Verify PDF was generated successfully
        pdf_data = pdf_response["data"]
        if not (isinstance(pdf_data, dict) and pdf_data.get("success") and "pdf_data" in pdf_data):
            self.log_test(
                "PDF Export with Logo - Generation", 
                False, 
                "Invalid PDF export response format", 
                pdf_data
            )
            return False
        
        # Verify PDF is valid
        try:
            pdf_bytes = base64.b64decode(pdf_data.get("pdf_data", ""))
            is_valid_pdf = pdf_bytes.startswith(b'%PDF')
            
            if not is_valid_pdf:
                self.log_test(
                    "PDF Export with Logo - Generation", 
                    False, 
                    "Generated PDF data is not valid PDF format", 
                    {"pdf_size": len(pdf_bytes)}
                )
                return False
        except Exception as e:
            self.log_test(
                "PDF Export with Logo - Generation", 
                False, 
                f"Error validating PDF data: {str(e)}", 
                {"pdf_data_length": len(pdf_data.get("pdf_data", ""))}
            )
            return False
        
        # Now check if PDF logo URL is still preserved after PDF generation
        await asyncio.sleep(1)  # Wait for any potential async operations
        
        get_response = await self.make_request("GET", "/admin/settings")
        
        if get_response["success"]:
            data = get_response["data"]
            if isinstance(data, dict):
                saved_pdf_logo_url = data.get("pdf_logo_url", "")
                
                if saved_pdf_logo_url == self.test_logo_urls[0]:
                    self.log_test(
                        "PDF Export with Logo - No Reset Verification",
                        True,
                        f"PDF logo URL preserved after PDF generation: {saved_pdf_logo_url}",
                        {
                            "pdf_generated": True,
                            "pdf_size": len(pdf_bytes),
                            "items_count": pdf_data.get("items_count", 0),
                            "total_value": pdf_data.get("total_value", 0),
                            "logo_url_preserved": saved_pdf_logo_url
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "PDF Export with Logo - No Reset Verification", 
                        False, 
                        f"PDF logo URL was reset after PDF generation! Expected: {self.test_logo_urls[0]}, Got: {saved_pdf_logo_url}", 
                        {"expected_url": self.test_logo_urls[0], "actual_url": saved_pdf_logo_url}
                    )
                    return False
            else:
                self.log_test(
                    "PDF Export with Logo - No Reset Verification", 
                    False, 
                    "Invalid settings response format after PDF generation", 
                    data
                )
                return False
        else:
            self.log_test(
                "PDF Export with Logo - No Reset Verification", 
                False, 
                f"Settings GET after PDF generation failed: {get_response['status']}", 
                get_response["data"]
            )
            return False
    
    async def test_4_multiple_save_cycles(self):
        """Test 4: Multiple GET/PUT operations to verify pdf_logo_url persists through multiple save cycles"""
        print("\n🔍 TEST 4: Multiple Save Cycles Persistence")
        
        success_count = 0
        total_cycles = 3
        
        for cycle in range(total_cycles):
            print(f"   Cycle {cycle + 1}/{total_cycles}: Testing with {self.test_logo_urls[cycle]}")
            
            # GET current settings
            get_response = await self.make_request("GET", "/admin/settings")
            if not get_response["success"]:
                self.log_test(
                    f"Multiple Save Cycles - Cycle {cycle + 1} GET", 
                    False, 
                    f"GET request failed in cycle {cycle + 1}", 
                    get_response["data"]
                )
                continue
            
            # Update with different logo URL
            current_settings = get_response["data"]
            updated_settings = current_settings.copy()
            updated_settings["pdf_logo_url"] = self.test_logo_urls[cycle]
            
            # PUT updated settings
            put_response = await self.make_request("PUT", "/admin/settings", data=updated_settings)
            if not put_response["success"]:
                self.log_test(
                    f"Multiple Save Cycles - Cycle {cycle + 1} PUT", 
                    False, 
                    f"PUT request failed in cycle {cycle + 1}", 
                    put_response["data"]
                )
                continue
            
            # Wait for database write
            await asyncio.sleep(1)
            
            # Verify persistence
            verify_response = await self.make_request("GET", "/admin/settings")
            if verify_response["success"]:
                verify_data = verify_response["data"]
                if isinstance(verify_data, dict):
                    saved_url = verify_data.get("pdf_logo_url", "")
                    
                    if saved_url == self.test_logo_urls[cycle]:
                        success_count += 1
                        print(f"      ✅ Cycle {cycle + 1} successful: {saved_url}")
                    else:
                        print(f"      ❌ Cycle {cycle + 1} failed: Expected {self.test_logo_urls[cycle]}, Got {saved_url}")
                else:
                    print(f"      ❌ Cycle {cycle + 1} failed: Invalid response format")
            else:
                print(f"      ❌ Cycle {cycle + 1} failed: Verification GET failed")
        
        # Log overall result
        if success_count == total_cycles:
            self.log_test(
                "Multiple Save Cycles - Overall",
                True,
                f"All {total_cycles} save cycles successful - pdf_logo_url persists correctly through multiple operations",
                {"successful_cycles": success_count, "total_cycles": total_cycles}
            )
            return True
        else:
            self.log_test(
                "Multiple Save Cycles - Overall", 
                False, 
                f"Only {success_count}/{total_cycles} save cycles successful - data loss detected", 
                {"successful_cycles": success_count, "total_cycles": total_cycles}
            )
            return False
    
    async def test_5_concurrent_operations(self):
        """Test 5: Concurrent operations to verify no race conditions cause data loss"""
        print("\n🔍 TEST 5: Concurrent Operations Test")
        
        # Set initial logo URL
        get_response = await self.make_request("GET", "/admin/settings")
        if not get_response["success"]:
            self.log_test(
                "Concurrent Operations - Setup", 
                False, 
                "Could not get initial settings for concurrent test", 
                get_response["data"]
            )
            return False
        
        initial_settings = get_response["data"]
        test_logo_url = "https://example.com/concurrent-test-logo.png"
        
        # Update settings with test logo
        updated_settings = initial_settings.copy()
        updated_settings["pdf_logo_url"] = test_logo_url
        
        put_response = await self.make_request("PUT", "/admin/settings", data=updated_settings)
        if not put_response["success"]:
            self.log_test(
                "Concurrent Operations - Setup", 
                False, 
                "Could not set initial logo for concurrent test", 
                put_response["data"]
            )
            return False
        
        await asyncio.sleep(1)
        
        # Perform concurrent GET operations
        concurrent_tasks = []
        for i in range(5):
            task = self.make_request("GET", "/admin/settings")
            concurrent_tasks.append(task)
        
        # Execute concurrent requests
        concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        
        # Verify all concurrent requests returned the same logo URL
        success_count = 0
        for i, result in enumerate(concurrent_results):
            if isinstance(result, dict) and result.get("success"):
                data = result.get("data", {})
                if isinstance(data, dict):
                    saved_url = data.get("pdf_logo_url", "")
                    if saved_url == test_logo_url:
                        success_count += 1
                    else:
                        print(f"      ❌ Concurrent request {i+1} returned wrong URL: {saved_url}")
                else:
                    print(f"      ❌ Concurrent request {i+1} returned invalid data format")
            else:
                print(f"      ❌ Concurrent request {i+1} failed: {result}")
        
        if success_count == 5:
            self.log_test(
                "Concurrent Operations - GET Consistency",
                True,
                f"All 5 concurrent GET requests returned consistent pdf_logo_url: {test_logo_url}",
                {"successful_requests": success_count, "total_requests": 5}
            )
            return True
        else:
            self.log_test(
                "Concurrent Operations - GET Consistency", 
                False, 
                f"Only {success_count}/5 concurrent requests returned consistent data", 
                {"successful_requests": success_count, "total_requests": 5}
            )
            return False
    
    async def test_6_restore_original_settings(self):
        """Test 6: Restore original settings to clean up test data"""
        print("\n🔍 TEST 6: Restore Original Settings")
        
        if not self.original_settings:
            self.log_test(
                "Restore Original Settings", 
                False, 
                "No original settings available for restoration", 
                None
            )
            return False
        
        # Restore original settings
        put_response = await self.make_request("PUT", "/admin/settings", data=self.original_settings)
        
        if put_response["success"]:
            # Verify restoration
            await asyncio.sleep(1)
            get_response = await self.make_request("GET", "/admin/settings")
            
            if get_response["success"]:
                data = get_response["data"]
                if isinstance(data, dict):
                    restored_url = data.get("pdf_logo_url", "")
                    original_url = self.original_settings.get("pdf_logo_url", "")
                    
                    if restored_url == original_url:
                        self.log_test(
                            "Restore Original Settings",
                            True,
                            f"Successfully restored original pdf_logo_url: '{original_url}'",
                            {"restored_url": restored_url, "original_url": original_url}
                        )
                        return True
                    else:
                        self.log_test(
                            "Restore Original Settings", 
                            False, 
                            f"Restoration verification failed. Expected: '{original_url}', Got: '{restored_url}'", 
                            {"restored_url": restored_url, "original_url": original_url}
                        )
                        return False
                else:
                    self.log_test(
                        "Restore Original Settings", 
                        False, 
                        "Invalid response format during restoration verification", 
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Restore Original Settings", 
                    False, 
                    f"Restoration verification GET failed: {get_response['status']}", 
                    get_response["data"]
                )
                return False
        else:
            self.log_test(
                "Restore Original Settings", 
                False, 
                f"Restoration PUT request failed: {put_response['status']}", 
                put_response["data"]
            )
            return False
    
    # ==== MAIN TEST EXECUTION ====
    
    async def run_all_tests(self):
        """Run all PDF logo reset issue tests"""
        print("🚀 Starting Cataloro Marketplace PDF Logo Reset Issue Testing...")
        print(f"📡 Testing against: {BACKEND_URL}")
        print("=" * 80)
        print("🎯 FOCUS: Verifying PDF logo no longer resets after save operations")
        print("📋 TESTS: Settings cycles, PDF export integration, persistence verification")
        
        # Execute tests in sequence
        test_results = []
        
        test_results.append(await self.test_1_settings_cycle_basic())
        test_results.append(await self.test_2_settings_cycle_put_verify())
        test_results.append(await self.test_3_pdf_export_with_logo())
        test_results.append(await self.test_4_multiple_save_cycles())
        test_results.append(await self.test_5_concurrent_operations())
        test_results.append(await self.test_6_restore_original_settings())
        
        # Print summary
        self.print_summary()
        
        return all(test_results)
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📋 PDF LOGO RESET ISSUE TESTING SUMMARY")
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
        
        print(f"\n🎯 PDF LOGO RESET ISSUE VERIFICATION:")
        print(f"   • Settings Cycle (GET → PUT → GET): {'✅' if any('Settings Cycle' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • PDF Export No Reset: {'✅' if any('PDF Export with Logo' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Multiple Save Cycles: {'✅' if any('Multiple Save Cycles' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Concurrent Operations: {'✅' if any('Concurrent Operations' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        
        # Determine overall status
        core_tests_passed = sum(1 for t in self.test_results if t['success'] and any(keyword in t['test'] for keyword in ['Settings Cycle', 'PDF Export', 'Multiple Save Cycles']))
        
        if core_tests_passed >= 3:
            print(f"\n🎉 PDF LOGO RESET ISSUE RESOLVED! The PDF logo persists correctly through all operations.")
        elif core_tests_passed >= 2:
            print(f"\n⚠️  MOSTLY RESOLVED with {3-core_tests_passed} minor issue(s).")
        else:
            print(f"\n🚨 PDF LOGO RESET ISSUE STILL EXISTS - {3-core_tests_passed} core tests failed.")

async def main():
    """Main test execution"""
    tester = PDFLogoResetTester()
    
    try:
        await tester.setup()
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        sys.exit(1)
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())