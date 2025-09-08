#!/usr/bin/env python3
"""
URGENT LISTINGS FUNCTIONALITY TESTING
Testing Agent: Comprehensive testing of listings endpoints and marketplace functionality
Focus: Critical bug investigation for broken listings functionality
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

class ListingsTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        self.test_listings = []
        self.auth_token = None
        
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
            
    async def make_request(self, method, endpoint, data=None, params=None, headers=None):
        """Make HTTP request with error handling"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            # Add auth headers if available
            if headers is None:
                headers = {}
            if self.auth_token:
                headers['Authorization'] = f"Bearer {self.auth_token}"
            
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    return await response.json(), response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params, headers=headers) as response:
                    return await response.json(), response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, params=params, headers=headers) as response:
                    return await response.json(), response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url, params=params, headers=headers) as response:
                    return await response.json(), response.status
                    
        except Exception as e:
            return {"error": str(e)}, 500
            
    async def setup_authentication(self):
        """Setup authentication for testing"""
        print("\n🔐 Setting up authentication...")
        
        # Login as admin user
        admin_login_response, admin_status = await self.make_request("POST", "/auth/login", {
            "email": "admin@cataloro.com",
            "password": "admin123"
        })
        
        if admin_status == 200 and "user" in admin_login_response:
            admin_user = admin_login_response["user"]
            self.test_users.append(admin_user)
            self.auth_token = admin_login_response.get("token")
            self.log_result("Admin Authentication", True, f"Admin user logged in: {admin_user.get('username', 'admin')}")
        else:
            self.log_result("Admin Authentication", False, f"Status: {admin_status}", str(admin_login_response))
        
        # Login as demo user
        demo_login_response, demo_status = await self.make_request("POST", "/auth/login", {
            "email": "user@cataloro.com",
            "password": "demo123"
        })
        
        if demo_status == 200 and "user" in demo_login_response:
            demo_user = demo_login_response["user"]
            self.test_users.append(demo_user)
            self.log_result("Demo User Authentication", True, f"Demo user logged in: {demo_user.get('username', 'demo')}")
        else:
            self.log_result("Demo User Authentication", False, f"Status: {demo_status}", str(demo_login_response))
        
        print(f"✅ Authentication setup complete: {len(self.test_users)} users authenticated")
                
    async def test_listings_endpoints(self):
        """Test all listings endpoints comprehensively"""
        print("\n📋 Testing Listings Endpoints...")
        
        # Test 1: GET /api/listings - Retrieve all listings
        await self.test_get_listings()
        
        # Test 2: POST /api/listings - Create new listing
        await self.test_create_listing()
        
        # Test 3: GET /api/listings/{id} - Get individual listing
        await self.test_get_individual_listing()
        
        # Test 4: PUT /api/listings/{id} - Update listing
        await self.test_update_listing()
        
        # Test 5: DELETE /api/listings/{id} - Delete listing
        await self.test_delete_listing()
        
        # Test 6: Browse marketplace endpoint
        await self.test_browse_marketplace()
        
    async def test_get_listings(self):
        """Test GET /api/listings endpoint"""
        try:
            response, status = await self.make_request("GET", "/listings")
            
            if status == 200:
                if isinstance(response, list):
                    self.log_result("GET /api/listings", True, f"Retrieved {len(response)} listings")
                    
                    # Store some listings for further testing
                    if response:
                        self.test_listings.extend(response[:3])  # Store first 3 for testing
                        
                        # Validate listing structure
                        first_listing = response[0]
                        required_fields = ['id', 'title', 'price', 'seller_id']
                        missing_fields = [field for field in required_fields if field not in first_listing]
                        
                        if not missing_fields:
                            self.log_result("Listing Data Structure", True, f"All required fields present: {required_fields}")
                        else:
                            self.log_result("Listing Data Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_result("GET /api/listings", True, "No listings found (empty marketplace)")
                else:
                    self.log_result("GET /api/listings", False, f"Expected list, got: {type(response)}")
            else:
                self.log_result("GET /api/listings", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("GET /api/listings", False, f"Request failed: {str(e)}")
            
    async def test_create_listing(self):
        """Test POST /api/listings endpoint"""
        if not self.test_users:
            self.log_result("Create Listing", False, "No authenticated users available")
            return
            
        user = self.test_users[0]  # Use admin user
        
        # Create test listing data
        test_listing = {
            "title": "Test Catalytic Converter - BMW 320d",
            "description": "High-quality catalytic converter from BMW 320d, excellent condition",
            "price": 450.00,
            "category": "Automotive",
            "condition": "Used - Excellent",
            "seller_id": user["id"],
            "images": ["https://example.com/image1.jpg"],
            "tags": ["BMW", "catalytic converter", "automotive"],
            "features": ["OEM quality", "Tested and verified"],
            "ceramic_weight": 1.2,
            "pt_ppm": 1200,
            "pd_ppm": 800,
            "rh_ppm": 150
        }
        
        try:
            response, status = await self.make_request("POST", "/listings", test_listing)
            
            if status in [200, 201]:
                if "id" in response:
                    listing_id = response["id"]
                    self.test_listings.append(response)
                    self.log_result("POST /api/listings", True, f"Created listing with ID: {listing_id}")
                    
                    # Validate created listing data
                    if response.get("title") == test_listing["title"]:
                        self.log_result("Listing Creation - Data Integrity", True, "Created listing matches input data")
                    else:
                        self.log_result("Listing Creation - Data Integrity", False, "Created listing data mismatch")
                else:
                    self.log_result("POST /api/listings", False, "No ID returned in response")
            else:
                self.log_result("POST /api/listings", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("POST /api/listings", False, f"Request failed: {str(e)}")
            
    async def test_get_individual_listing(self):
        """Test GET /api/listings/{id} endpoint"""
        if not self.test_listings:
            self.log_result("GET Individual Listing", False, "No test listings available")
            return
            
        listing = self.test_listings[0]
        listing_id = listing.get("id")
        
        if not listing_id:
            self.log_result("GET Individual Listing", False, "No listing ID available")
            return
            
        try:
            response, status = await self.make_request("GET", f"/listings/{listing_id}")
            
            if status == 200:
                if response.get("id") == listing_id:
                    self.log_result("GET /api/listings/{id}", True, f"Retrieved listing: {response.get('title', 'Unknown')}")
                    
                    # Validate listing details
                    if "title" in response and "price" in response and "seller_id" in response:
                        self.log_result("Individual Listing - Data Completeness", True, "All essential fields present")
                    else:
                        self.log_result("Individual Listing - Data Completeness", False, "Missing essential fields")
                else:
                    self.log_result("GET /api/listings/{id}", False, "Returned listing ID mismatch")
            else:
                self.log_result("GET /api/listings/{id}", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("GET /api/listings/{id}", False, f"Request failed: {str(e)}")
            
    async def test_update_listing(self):
        """Test PUT /api/listings/{id} endpoint"""
        if not self.test_listings:
            self.log_result("Update Listing", False, "No test listings available")
            return
            
        listing = self.test_listings[0]
        listing_id = listing.get("id")
        
        if not listing_id:
            self.log_result("Update Listing", False, "No listing ID available")
            return
            
        # Update data
        update_data = {
            "title": "Updated Test Listing - BMW 320d Premium",
            "price": 475.00,
            "description": "Updated description with premium features"
        }
        
        try:
            response, status = await self.make_request("PUT", f"/listings/{listing_id}", update_data)
            
            if status == 200:
                if response.get("title") == update_data["title"]:
                    self.log_result("PUT /api/listings/{id}", True, f"Updated listing: {response.get('title')}")
                else:
                    self.log_result("PUT /api/listings/{id}", False, "Update data not reflected in response")
            else:
                self.log_result("PUT /api/listings/{id}", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("PUT /api/listings/{id}", False, f"Request failed: {str(e)}")
            
    async def test_delete_listing(self):
        """Test DELETE /api/listings/{id} endpoint"""
        if len(self.test_listings) < 2:
            self.log_result("Delete Listing", False, "Insufficient test listings for deletion test")
            return
            
        # Use the last created listing for deletion
        listing = self.test_listings[-1]
        listing_id = listing.get("id")
        
        if not listing_id:
            self.log_result("Delete Listing", False, "No listing ID available for deletion")
            return
            
        try:
            response, status = await self.make_request("DELETE", f"/listings/{listing_id}")
            
            if status in [200, 204]:
                self.log_result("DELETE /api/listings/{id}", True, f"Deleted listing: {listing_id}")
                
                # Verify deletion by trying to retrieve the listing
                verify_response, verify_status = await self.make_request("GET", f"/listings/{listing_id}")
                
                if verify_status == 404:
                    self.log_result("Delete Verification", True, "Listing successfully deleted (404 on retrieval)")
                else:
                    self.log_result("Delete Verification", False, f"Listing still exists after deletion (status: {verify_status})")
            else:
                self.log_result("DELETE /api/listings/{id}", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("DELETE /api/listings/{id}", False, f"Request failed: {str(e)}")
            
    async def test_browse_marketplace(self):
        """Test /api/marketplace/browse endpoint"""
        try:
            # Test basic browse
            response, status = await self.make_request("GET", "/marketplace/browse")
            
            if status == 200:
                if isinstance(response, list):
                    self.log_result("Browse Marketplace", True, f"Browse returned {len(response)} listings")
                    
                    # Test with filters
                    await self.test_browse_with_filters()
                    
                    # Test search functionality
                    await self.test_search_functionality()
                else:
                    self.log_result("Browse Marketplace", False, f"Expected list, got: {type(response)}")
            else:
                self.log_result("Browse Marketplace", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("Browse Marketplace", False, f"Request failed: {str(e)}")
            
    async def test_browse_with_filters(self):
        """Test browse endpoint with filters"""
        try:
            # Test price filter
            params = {
                "price_from": 100,
                "price_to": 500,
                "page": 1,
                "limit": 10
            }
            
            response, status = await self.make_request("GET", "/marketplace/browse", params=params)
            
            if status == 200:
                self.log_result("Browse with Filters", True, f"Filtered browse returned {len(response)} listings")
                
                # Validate price filtering
                if response:
                    for listing in response:
                        price = listing.get("price", 0)
                        if not (100 <= price <= 500):
                            self.log_result("Price Filter Validation", False, f"Listing price {price} outside filter range")
                            return
                    self.log_result("Price Filter Validation", True, "All listings within price range")
            else:
                self.log_result("Browse with Filters", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("Browse with Filters", False, f"Request failed: {str(e)}")
            
    async def test_search_functionality(self):
        """Test search endpoints"""
        try:
            # Test search suggestions
            response, status = await self.make_request("GET", "/marketplace/search/suggestions", params={"q": "BMW"})
            
            if status == 200:
                suggestions = response.get("suggestions", [])
                self.log_result("Search Suggestions", True, f"Got {len(suggestions)} suggestions for 'BMW'")
            else:
                self.log_result("Search Suggestions", False, f"Status: {status}", str(response))
                
            # Test advanced search
            search_params = {
                "q": "catalytic",
                "category": "Automotive",
                "price_min": 100,
                "price_max": 1000,
                "page": 1,
                "limit": 10
            }
            
            response, status = await self.make_request("GET", "/marketplace/search", params=search_params)
            
            if status == 200:
                results = response.get("results", [])
                total = response.get("total", 0)
                self.log_result("Advanced Search", True, f"Search returned {len(results)} results (total: {total})")
            else:
                self.log_result("Advanced Search", False, f"Status: {status}", str(response))
                
        except Exception as e:
            self.log_result("Search Functionality", False, f"Request failed: {str(e)}")
            
    async def test_database_connectivity(self):
        """Test database connectivity for listings"""
        print("\n🗄️ Testing Database Connectivity...")
        
        try:
            # Test health endpoint to verify database connection
            response, status = await self.make_request("GET", "/health")
            
            if status == 200:
                self.log_result("Database Health Check", True, f"Backend healthy: {response.get('app', 'Unknown')}")
            else:
                self.log_result("Database Health Check", False, f"Status: {status}")
                
            # Test performance metrics to check database stats
            response, status = await self.make_request("GET", "/admin/performance")
            
            if status == 200:
                db_info = response.get("database", {})
                collections = response.get("collections", {})
                
                if "listings" in collections:
                    listings_stats = collections["listings"]
                    doc_count = listings_stats.get("document_count", 0)
                    self.log_result("Listings Collection", True, f"Found {doc_count} listings in database")
                else:
                    self.log_result("Listings Collection", False, "Listings collection not found in database stats")
                    
                self.log_result("Database Performance", True, f"Database size: {db_info.get('total_size', 0)} bytes")
            else:
                self.log_result("Database Performance", False, f"Status: {status}")
                
        except Exception as e:
            self.log_result("Database Connectivity", False, f"Test failed: {str(e)}")
            
    async def test_data_validation(self):
        """Test data validation for listing creation"""
        print("\n✅ Testing Data Validation...")
        
        if not self.test_users:
            self.log_result("Data Validation", False, "No authenticated users available")
            return
            
        user = self.test_users[0]
        
        # Test 1: Missing required fields
        invalid_listing = {
            "description": "Missing title and price"
        }
        
        response, status = await self.make_request("POST", "/listings", invalid_listing)
        
        if status in [400, 422]:
            self.log_result("Validation - Missing Fields", True, f"Properly rejected missing fields (status: {status})")
        else:
            self.log_result("Validation - Missing Fields", False, f"Should reject missing fields, got status: {status}")
            
        # Test 2: Invalid data types
        invalid_types = {
            "title": "Valid Title",
            "price": "not_a_number",  # Should be float
            "seller_id": user["id"]
        }
        
        response, status = await self.make_request("POST", "/listings", invalid_types)
        
        if status in [400, 422]:
            self.log_result("Validation - Invalid Types", True, f"Properly rejected invalid types (status: {status})")
        else:
            self.log_result("Validation - Invalid Types", False, f"Should reject invalid types, got status: {status}")
            
        # Test 3: Valid listing creation
        valid_listing = {
            "title": "Valid Test Listing",
            "description": "This is a valid test listing",
            "price": 299.99,
            "category": "Test Category",
            "condition": "New",
            "seller_id": user["id"]
        }
        
        response, status = await self.make_request("POST", "/listings", valid_listing)
        
        if status in [200, 201]:
            self.log_result("Validation - Valid Data", True, f"Accepted valid listing (status: {status})")
        else:
            self.log_result("Validation - Valid Data", False, f"Should accept valid data, got status: {status}")
            
    async def test_error_analysis(self):
        """Analyze specific error messages and response codes"""
        print("\n🔍 Testing Error Analysis...")
        
        # Test non-existent listing
        fake_id = str(uuid.uuid4())
        response, status = await self.make_request("GET", f"/listings/{fake_id}")
        
        if status == 404:
            self.log_result("Error Analysis - 404 Handling", True, "Properly returns 404 for non-existent listing")
        else:
            self.log_result("Error Analysis - 404 Handling", False, f"Expected 404, got {status}")
            
        # Test invalid endpoint
        response, status = await self.make_request("GET", "/listings/invalid/endpoint")
        
        if status in [404, 405]:
            self.log_result("Error Analysis - Invalid Endpoint", True, f"Properly handles invalid endpoint (status: {status})")
        else:
            self.log_result("Error Analysis - Invalid Endpoint", False, f"Unexpected status for invalid endpoint: {status}")
            
        # Test server error handling
        malformed_data = {"invalid": "json", "structure": {"nested": {"too": {"deep": True}}}}
        response, status = await self.make_request("POST", "/listings", malformed_data)
        
        if status >= 400:
            error_detail = response.get("detail", response.get("error", "No error detail"))
            self.log_result("Error Analysis - Server Errors", True, f"Server error handled: {error_detail}")
        else:
            self.log_result("Error Analysis - Server Errors", False, f"Should return error for malformed data, got {status}")
            
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
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🧪 LISTINGS FUNCTIONALITY TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n❌ CRITICAL FAILURES:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
                    
        print(f"\n🎯 TESTED ENDPOINTS:")
        print(f"   • GET /api/listings - Retrieve all listings")
        print(f"   • POST /api/listings - Create new listing")
        print(f"   • GET /api/listings/{{id}} - Get individual listing")
        print(f"   • PUT /api/listings/{{id}} - Update listing")
        print(f"   • DELETE /api/listings/{{id}} - Delete listing")
        print(f"   • GET /api/marketplace/browse - Browse marketplace")
        print(f"   • GET /api/marketplace/search - Search functionality")
        
        print(f"\n📊 TEST CATEGORIES:")
        endpoint_tests = [r for r in self.test_results if "api/listings" in r["test"] or "GET" in r["test"] or "POST" in r["test"]]
        auth_tests = [r for r in self.test_results if "Authentication" in r["test"]]
        db_tests = [r for r in self.test_results if "Database" in r["test"]]
        validation_tests = [r for r in self.test_results if "Validation" in r["test"]]
        error_tests = [r for r in self.test_results if "Error" in r["test"]]
        
        print(f"   • Endpoint Tests: {sum(1 for t in endpoint_tests if t['success'])}/{len(endpoint_tests)} passed")
        print(f"   • Authentication: {sum(1 for t in auth_tests if t['success'])}/{len(auth_tests)} passed")
        print(f"   • Database Tests: {sum(1 for t in db_tests if t['success'])}/{len(db_tests)} passed")
        print(f"   • Validation Tests: {sum(1 for t in validation_tests if t['success'])}/{len(validation_tests)} passed")
        print(f"   • Error Handling: {sum(1 for t in error_tests if t['success'])}/{len(error_tests)} passed")
        
        print(f"\n📋 TEST DATA:")
        print(f"   • Authenticated Users: {len(self.test_users)}")
        print(f"   • Test Listings Created: {len(self.test_listings)}")
        print(f"   • Backend URL: {BASE_URL}")
        
        # Identify critical issues
        critical_failures = []
        for result in self.test_results:
            if not result["success"] and any(keyword in result["test"] for keyword in ["GET /api/listings", "POST /api/listings", "Browse Marketplace", "Database"]):
                critical_failures.append(result["test"])
                
        if critical_failures:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   • {failure}")
            print(f"\n💡 RECOMMENDED ACTIONS:")
            print(f"   1. Check backend server logs for detailed error messages")
            print(f"   2. Verify MongoDB connection and listings collection")
            print(f"   3. Ensure all required endpoints are properly implemented")
            print(f"   4. Test authentication and authorization for listing operations")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED - Listings functionality appears to be working")
        
async def main():
    """Main test execution"""
    print("🚀 Starting URGENT Listings Functionality Testing")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("🔍 Focus: Critical bug investigation for broken listings functionality")
    print("="*80)
    
    tester = ListingsTester()
    
    try:
        await tester.setup_session()
        
        # Test backend health first
        await tester.test_backend_health()
        
        # Setup authentication
        await tester.setup_authentication()
        
        # Test database connectivity
        await tester.test_database_connectivity()
        
        # Test all listings endpoints
        await tester.test_listings_endpoints()
        
        # Test data validation
        await tester.test_data_validation()
        
        # Test error analysis
        await tester.test_error_analysis()
        
        # Print comprehensive summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())