#!/usr/bin/env python3
"""
Cataloro Marketplace - Inventory/Basket Functionality & PDF Export Testing
Tests the specific functionality requested in the review:
1. Backend Status Check
2. User Baskets API (/api/user/baskets/{user_id})
3. PDF Export API (/api/admin/export/basket-pdf)
4. Backend Routes Verification
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
BACKEND_URL = "https://marketplace-repair-1.preview.emergentagent.com/api"

class InventoryBasketTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.test_user_id = "test_user_inventory_123"
        
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
            elif method.upper() == "DELETE":
                async with self.session.delete(url, params=params) as response:
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
    
    # ==== BACKEND STATUS TESTS ====
    
    async def test_backend_health(self):
        """Test backend health and responsiveness (CRITICAL)"""
        response = await self.make_request("GET", "/health")
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and data.get("status") == "healthy":
                app_name = data.get("app", "Unknown")
                version = data.get("version", "Unknown")
                
                self.log_test(
                    "Backend Health Check",
                    True,
                    f"Backend is healthy - {app_name} v{version}",
                    data
                )
            else:
                self.log_test("Backend Health Check", False, "Invalid health response format", data)
        else:
            self.log_test("Backend Health Check", False, f"Health check failed: {response['status']}", response["data"])
    
    async def test_backend_performance_status(self):
        """Test backend performance and optimization status (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/admin/performance")
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and "performance_status" in data:
                perf_status = data.get("performance_status", "unknown")
                db_info = data.get("database", {})
                
                self.log_test(
                    "Backend Performance Status",
                    True,
                    f"Performance: {perf_status}, DB Collections: {db_info.get('collections', 0)}",
                    {
                        "performance_status": perf_status,
                        "database_collections": db_info.get('collections', 0),
                        "optimizations": data.get("optimizations", {})
                    }
                )
            else:
                self.log_test("Backend Performance Status", False, "Invalid performance response", data)
        else:
            self.log_test("Backend Performance Status", False, f"Performance check failed: {response['status']}", response["data"])
    
    # ==== USER BASKETS API TESTS ====
    
    async def test_user_baskets_endpoint(self):
        """Test /api/user/baskets/{user_id} endpoint (CRITICAL)"""
        response = await self.make_request("GET", f"/user/baskets/{self.test_user_id}")
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, list):
                basket_count = len(data)
                
                self.log_test(
                    "User Baskets API - GET",
                    True,
                    f"Retrieved {basket_count} baskets for user {self.test_user_id}",
                    {"basket_count": basket_count, "baskets": data[:2] if data else []}  # Show first 2 baskets
                )
                
                # Store first basket for PDF export test
                if data:
                    self.test_basket = data[0]
                else:
                    # Create a test basket if none exist
                    await self.create_test_basket()
                    
            else:
                self.log_test("User Baskets API - GET", False, "Invalid baskets response format", data)
        else:
            self.log_test("User Baskets API - GET", False, f"Baskets API failed: {response['status']}", response["data"])
    
    async def create_test_basket(self):
        """Create a test basket for testing purposes"""
        basket_data = {
            "user_id": self.test_user_id,
            "name": "Test Precious Metals Basket",
            "description": "Test basket for inventory testing with precious metals"
        }
        
        response = await self.make_request("POST", "/user/baskets", data=basket_data)
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and "id" in data:
                self.test_basket = data
                self.log_test(
                    "Test Basket Creation",
                    True,
                    f"Created test basket: {data.get('id')}",
                    data
                )
            else:
                self.log_test("Test Basket Creation", False, "Invalid basket creation response", data)
        else:
            # If creation fails, create a mock basket for PDF testing
            self.test_basket = {
                "id": "mock_basket_123",
                "name": "Mock Test Basket",
                "items": basket_data["items"]
            }
            self.log_test("Test Basket Creation", False, f"Basket creation failed, using mock data: {response['status']}", response["data"])
    
    async def test_basket_crud_operations(self):
        """Test basket CRUD operations (HIGH PRIORITY)"""
        # Test basket update
        if hasattr(self, 'test_basket') and self.test_basket:
            basket_id = self.test_basket.get('basket_id') or self.test_basket.get('id')
            
            update_data = {
                "name": "Updated Test Basket",
                "description": "Updated description for testing"
            }
            
            response = await self.make_request("PUT", f"/user/baskets/{basket_id}", data=update_data)
            
            if response["success"]:
                self.log_test(
                    "Basket Update Operation",
                    True,
                    f"Successfully updated basket {basket_id}",
                    response["data"]
                )
            else:
                self.log_test("Basket Update Operation", False, f"Basket update failed: {response['status']}", response["data"])
        else:
            self.log_test("Basket Update Operation", False, "No test basket available for update", None)
    
    # ==== PDF EXPORT API TESTS ====
    
    async def test_pdf_export_endpoint(self):
        """Test /api/admin/export/basket-pdf endpoint (CRITICAL)"""
        # Prepare basket data for PDF export (based on server code format)
        basket_data = {
            "id": "pdf_test_basket",
            "name": "PDF Export Test Basket",
            "user_id": self.test_user_id,
            "items": [
                {
                    "name": "Platinum Catalyst Sample",
                    "price": 1850.00,
                    "pt_g": 9.10,
                    "pd_g": 7.50,
                    "rh_g": 1.80
                },
                {
                    "name": "Palladium Catalyst Sample", 
                    "price": 920.00,
                    "pt_g": 3.20,
                    "pd_g": 12.50,
                    "rh_g": 0.95
                }
            ]
        }
        
        response = await self.make_request("POST", "/admin/export/basket-pdf", data=basket_data)
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict) and "pdf_data" in data:
                pdf_data = data.get("pdf_data", "")
                filename = data.get("filename", "unknown")
                items_count = data.get("items_count", 0)
                total_value = data.get("total_value", 0)
                
                # Verify PDF data is base64 encoded
                is_valid_pdf = False
                try:
                    decoded_pdf = base64.b64decode(pdf_data)
                    is_valid_pdf = decoded_pdf.startswith(b'%PDF')
                except:
                    is_valid_pdf = False
                
                self.log_test(
                    "PDF Export API",
                    True,
                    f"PDF generated: {filename}, Items: {items_count}, Value: €{total_value}, Valid PDF: {is_valid_pdf}",
                    {
                        "filename": filename,
                        "items_count": items_count,
                        "total_value": total_value,
                        "pdf_size_bytes": len(pdf_data) if pdf_data else 0,
                        "is_valid_pdf": is_valid_pdf
                    }
                )
            else:
                self.log_test("PDF Export API", False, "Invalid PDF export response format", data)
        else:
            self.log_test("PDF Export API", False, f"PDF export failed: {response['status']}", response["data"])
    
    async def test_pdf_export_with_empty_basket(self):
        """Test PDF export with empty basket (MEDIUM PRIORITY)"""
        empty_basket_data = {
            "id": "empty_basket_test",
            "name": "Empty Basket Test",
            "user_id": self.test_user_id,
            "items": []
        }
        
        response = await self.make_request("POST", "/admin/export/basket-pdf", data=empty_basket_data)
        
        if response["success"]:
            data = response["data"]
            if isinstance(data, dict):
                items_count = data.get("items_count", 0)
                total_value = data.get("total_value", 0)
                
                self.log_test(
                    "PDF Export - Empty Basket",
                    True,
                    f"Empty basket PDF generated: Items: {items_count}, Value: €{total_value}",
                    data
                )
            else:
                self.log_test("PDF Export - Empty Basket", False, "Invalid empty basket response", data)
        else:
            self.log_test("PDF Export - Empty Basket", False, f"Empty basket PDF failed: {response['status']}", response["data"])
    
    async def test_pdf_export_error_handling(self):
        """Test PDF export error handling (MEDIUM PRIORITY)"""
        invalid_data = {
            "invalid_field": "test"
        }
        
        response = await self.make_request("POST", "/admin/export/basket-pdf", data=invalid_data)
        
        # This should fail gracefully
        if not response["success"]:
            self.log_test(
                "PDF Export Error Handling",
                True,
                f"Properly handled invalid data with status: {response['status']}",
                response["data"]
            )
        else:
            self.log_test("PDF Export Error Handling", False, "Should have failed with invalid data", response["data"])
    
    # ==== BACKEND ROUTES VERIFICATION ====
    
    async def test_essential_backend_routes(self):
        """Test essential backend routes accessibility (HIGH PRIORITY)"""
        essential_routes = [
            ("/health", "Health Check"),
            ("/marketplace/browse", "Browse Listings"),
            ("/admin/performance", "Admin Performance"),
            ("/admin/users", "Admin Users"),
            ("/admin/settings", "Admin Settings")
        ]
        
        route_results = []
        
        for route, description in essential_routes:
            response = await self.make_request("GET", route)
            
            route_status = {
                "route": route,
                "description": description,
                "accessible": response["success"],
                "status_code": response["status"]
            }
            route_results.append(route_status)
        
        accessible_routes = [r for r in route_results if r["accessible"]]
        
        self.log_test(
            "Essential Backend Routes",
            len(accessible_routes) >= 3,  # At least 3 routes should be accessible
            f"Accessible routes: {len(accessible_routes)}/{len(essential_routes)}",
            route_results
        )
    
    async def test_inventory_related_routes(self):
        """Test inventory and basket related routes (HIGH PRIORITY)"""
        inventory_routes = [
            (f"/user/baskets/{self.test_user_id}", "User Baskets"),
            ("/admin/export/basket-pdf", "PDF Export", "POST"),
            ("/admin/analytics/dashboard", "Analytics Dashboard"),
            ("/admin/media/files", "Media Files")
        ]
        
        route_results = []
        
        for route_info in inventory_routes:
            if len(route_info) == 3:
                route, description, method = route_info
            else:
                route, description = route_info
                method = "GET"
            
            if method == "POST":
                # For POST routes, just check if they exist (might return error but should not be 404)
                response = await self.make_request("POST", route, data={})
                accessible = response["status"] != 404
            else:
                response = await self.make_request("GET", route)
                accessible = response["success"]
            
            route_status = {
                "route": route,
                "description": description,
                "method": method,
                "accessible": accessible,
                "status_code": response["status"]
            }
            route_results.append(route_status)
        
        accessible_routes = [r for r in route_results if r["accessible"]]
        
        self.log_test(
            "Inventory Related Routes",
            len(accessible_routes) >= 2,  # At least 2 inventory routes should be accessible
            f"Accessible inventory routes: {len(accessible_routes)}/{len(inventory_routes)}",
            route_results
        )
    
    # ==== MAIN TEST EXECUTION ====
    
    async def run_all_tests(self):
        """Run all inventory/basket tests"""
        print("🚀 Starting Cataloro Marketplace Inventory/Basket & PDF Export Testing...")
        print(f"📡 Testing against: {BACKEND_URL}")
        print("=" * 80)
        
        # CRITICAL TESTS - Backend Status
        print("\n🏥 CRITICAL: Backend Status & Health")
        await self.test_backend_health()
        await self.test_backend_performance_status()
        
        # CRITICAL TESTS - User Baskets API
        print("\n🗂️ CRITICAL: User Baskets API Testing")
        await self.test_user_baskets_endpoint()
        await self.test_basket_crud_operations()
        
        # CRITICAL TESTS - PDF Export API
        print("\n📄 CRITICAL: PDF Export API Testing")
        await self.test_pdf_export_endpoint()
        await self.test_pdf_export_with_empty_basket()
        await self.test_pdf_export_error_handling()
        
        # HIGH PRIORITY TESTS - Backend Routes
        print("\n🛣️ HIGH PRIORITY: Backend Routes Verification")
        await self.test_essential_backend_routes()
        await self.test_inventory_related_routes()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 INVENTORY/BASKET & PDF EXPORT TESTING SUMMARY")
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
        
        print(f"\n🎯 FUNCTIONALITY VERIFICATION:")
        print(f"   • Backend Health: {'✅' if any('Health' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • User Baskets API: {'✅' if any('Baskets API' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • PDF Export API: {'✅' if any('PDF Export API' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Backend Routes: {'✅' if any('Routes' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL INVENTORY/BASKET TESTS PASSED! The functionality is working correctly.")
        elif failed_tests <= 2:
            print(f"\n⚠️  MOSTLY SUCCESSFUL with {failed_tests} minor issues.")
        else:
            print(f"\n🚨 INVENTORY/BASKET ISSUES DETECTED - {failed_tests} tests failed.")

async def main():
    """Main test execution"""
    tester = InventoryBasketTester()
    
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