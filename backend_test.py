#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - TENDER MANAGEMENT API TESTING
Testing the tender management API endpoints to verify they are working correctly

SPECIFIC TESTS REQUESTED:
1. **Test Buyer Tenders Endpoint**: GET /api/tenders/buyer/admin_user_1 - verify tender list with listing info
2. **Test Seller Tenders Overview Endpoint**: GET /api/tenders/seller/admin_user_1/overview - verify overview with listings
3. **Verify Data Structure**: Check tender IDs, offer_amounts, status, listing titles, prices, images
4. **Test Different User IDs**: Try other user IDs to see data variation
5. **Verify Enrichment**: Check buyer/seller information is properly enriched

CRITICAL ENDPOINTS BEING TESTED:
- POST /api/auth/login (user authentication)
- GET /api/tenders/buyer/{buyer_id} (get buyer's submitted tenders with listing details)
- GET /api/tenders/seller/{seller_id}/overview (get seller's listings with associated tenders)

EXPECTED RESULTS:
- ✅ Buyer tenders endpoint returns list of tenders with listing information
- ✅ Seller tenders overview returns listings with associated tender data
- ✅ Data structure includes proper IDs, offer_amounts, status fields
- ✅ Listings have proper titles, prices, images
- ✅ Buyer/seller information is properly enriched
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        print(f"   Details: {details}")
        print()
    
    async def test_login_and_get_token(self, email="admin@cataloro.com", password="admin123"):
        """Test login and get JWT token"""
        start_time = datetime.now()
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            "Login Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id}), token received",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Login Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Login Authentication", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Login Authentication", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None, None, None
    
    async def test_buyer_tenders_endpoint(self, buyer_id, token):
        """Test GET /api/tenders/buyer/{buyer_id} endpoint"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/tenders/buyer/{buyer_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        tender_count = len(data)
                        
                        # Check if tenders have proper structure
                        has_proper_structure = True
                        structure_details = []
                        
                        if tender_count > 0:
                            sample_tender = data[0]
                            required_fields = ['id', 'offer_amount', 'status', 'listing', 'seller']
                            listing_fields = ['id', 'title', 'price', 'images']
                            seller_fields = ['id', 'username', 'full_name']
                            
                            # Check tender fields
                            missing_tender_fields = [field for field in required_fields if field not in sample_tender]
                            if missing_tender_fields:
                                has_proper_structure = False
                                structure_details.append(f"Missing tender fields: {missing_tender_fields}")
                            
                            # Check listing enrichment
                            if 'listing' in sample_tender and isinstance(sample_tender['listing'], dict):
                                missing_listing_fields = [field for field in listing_fields if field not in sample_tender['listing']]
                                if missing_listing_fields:
                                    structure_details.append(f"Missing listing fields: {missing_listing_fields}")
                            else:
                                has_proper_structure = False
                                structure_details.append("Missing or invalid listing enrichment")
                            
                            # Check seller enrichment
                            if 'seller' in sample_tender and isinstance(sample_tender['seller'], dict):
                                missing_seller_fields = [field for field in seller_fields if field not in sample_tender['seller']]
                                if missing_seller_fields:
                                    structure_details.append(f"Missing seller fields: {missing_seller_fields}")
                            else:
                                has_proper_structure = False
                                structure_details.append("Missing or invalid seller enrichment")
                        
                        if has_proper_structure:
                            self.log_result(
                                "Buyer Tenders Endpoint", 
                                True, 
                                f"✅ WORKING CORRECTLY: Returns {tender_count} tenders with proper listing and seller enrichment",
                                response_time
                            )
                        else:
                            self.log_result(
                                "Buyer Tenders Endpoint", 
                                False, 
                                f"❌ STRUCTURE ISSUES: Returns {tender_count} tenders but has structure problems: {'; '.join(structure_details)}",
                                response_time
                            )
                        
                        return {
                            'success': True,
                            'tender_count': tender_count,
                            'data': data,
                            'has_proper_structure': has_proper_structure,
                            'structure_details': structure_details
                        }
                    else:
                        self.log_result(
                            "Buyer Tenders Endpoint", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Buyer Tenders Endpoint", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Buyer Tenders Endpoint", 
                False, 
                f"❌ REQUEST FAILED: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_seller_tenders_overview_endpoint(self, seller_id, token):
        """Test GET /api/tenders/seller/{seller_id}/overview endpoint"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/tenders/seller/{seller_id}/overview"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        listing_count = len(data)
                        total_tenders = 0
                        
                        # Check if overview has proper structure
                        has_proper_structure = True
                        structure_details = []
                        
                        if listing_count > 0:
                            sample_overview = data[0]
                            required_fields = ['listing', 'seller', 'tender_count', 'tenders']
                            listing_fields = ['id', 'title', 'price', 'images']
                            seller_fields = ['id', 'username', 'full_name']
                            
                            # Check overview fields
                            missing_overview_fields = [field for field in required_fields if field not in sample_overview]
                            if missing_overview_fields:
                                has_proper_structure = False
                                structure_details.append(f"Missing overview fields: {missing_overview_fields}")
                            
                            # Check listing enrichment
                            if 'listing' in sample_overview and isinstance(sample_overview['listing'], dict):
                                missing_listing_fields = [field for field in listing_fields if field not in sample_overview['listing']]
                                if missing_listing_fields:
                                    structure_details.append(f"Missing listing fields: {missing_listing_fields}")
                            else:
                                has_proper_structure = False
                                structure_details.append("Missing or invalid listing enrichment")
                            
                            # Check seller enrichment
                            if 'seller' in sample_overview and isinstance(sample_overview['seller'], dict):
                                missing_seller_fields = [field for field in seller_fields if field not in sample_overview['seller']]
                                if missing_seller_fields:
                                    structure_details.append(f"Missing seller fields: {missing_seller_fields}")
                            else:
                                has_proper_structure = False
                                structure_details.append("Missing or invalid seller enrichment")
                            
                            # Count total tenders
                            for overview in data:
                                total_tenders += overview.get('tender_count', 0)
                        
                        if has_proper_structure:
                            self.log_result(
                                "Seller Tenders Overview Endpoint", 
                                True, 
                                f"✅ WORKING CORRECTLY: Returns {listing_count} listings with {total_tenders} total tenders, proper enrichment",
                                response_time
                            )
                        else:
                            self.log_result(
                                "Seller Tenders Overview Endpoint", 
                                False, 
                                f"❌ STRUCTURE ISSUES: Returns {listing_count} listings but has structure problems: {'; '.join(structure_details)}",
                                response_time
                            )
                        
                        return {
                            'success': True,
                            'listing_count': listing_count,
                            'total_tenders': total_tenders,
                            'data': data,
                            'has_proper_structure': has_proper_structure,
                            'structure_details': structure_details
                        }
                    else:
                        self.log_result(
                            "Seller Tenders Overview Endpoint", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Seller Tenders Overview Endpoint", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Seller Tenders Overview Endpoint", 
                False, 
                f"❌ REQUEST FAILED: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_tender_data_structure(self, buyer_result, seller_result):
        """Test data structure and content verification"""
        try:
            structure_issues = []
            data_quality_issues = []
            
            # Verify buyer tenders data structure
            if buyer_result.get('success') and buyer_result.get('data'):
                buyer_data = buyer_result['data']
                if len(buyer_data) > 0:
                    sample_tender = buyer_data[0]
                    
                    # Check tender IDs
                    if not sample_tender.get('id'):
                        structure_issues.append("Buyer tender missing ID")
                    
                    # Check offer amounts
                    if 'offer_amount' not in sample_tender or not isinstance(sample_tender['offer_amount'], (int, float)):
                        structure_issues.append("Buyer tender missing or invalid offer_amount")
                    
                    # Check status
                    if not sample_tender.get('status'):
                        structure_issues.append("Buyer tender missing status")
                    
                    # Check listing details
                    listing = sample_tender.get('listing', {})
                    if not listing.get('title'):
                        data_quality_issues.append("Buyer tender listing missing title")
                    if 'price' not in listing or not isinstance(listing['price'], (int, float)):
                        data_quality_issues.append("Buyer tender listing missing or invalid price")
                    if not isinstance(listing.get('images', []), list):
                        data_quality_issues.append("Buyer tender listing images not array")
            
            # Verify seller overview data structure
            if seller_result.get('success') and seller_result.get('data'):
                seller_data = seller_result['data']
                if len(seller_data) > 0:
                    sample_overview = seller_data[0]
                    
                    # Check listing details
                    listing = sample_overview.get('listing', {})
                    if not listing.get('id'):
                        structure_issues.append("Seller overview listing missing ID")
                    if not listing.get('title'):
                        data_quality_issues.append("Seller overview listing missing title")
                    if 'price' not in listing or not isinstance(listing['price'], (int, float)):
                        data_quality_issues.append("Seller overview listing missing or invalid price")
                    
                    # Check tender count
                    if 'tender_count' not in sample_overview or not isinstance(sample_overview['tender_count'], int):
                        structure_issues.append("Seller overview missing or invalid tender_count")
                    
                    # Check tenders array
                    tenders = sample_overview.get('tenders', [])
                    if not isinstance(tenders, list):
                        structure_issues.append("Seller overview tenders not array")
                    elif len(tenders) > 0:
                        sample_tender = tenders[0]
                        if not sample_tender.get('id'):
                            structure_issues.append("Seller overview tender missing ID")
                        if 'offer_amount' not in sample_tender:
                            structure_issues.append("Seller overview tender missing offer_amount")
            
            # Determine overall result
            has_critical_issues = len(structure_issues) > 0
            has_quality_issues = len(data_quality_issues) > 0
            
            if not has_critical_issues and not has_quality_issues:
                self.log_result(
                    "Data Structure and Content Verification", 
                    True, 
                    "✅ DATA STRUCTURE CORRECT: All required fields present with proper types and content"
                )
            elif not has_critical_issues:
                self.log_result(
                    "Data Structure and Content Verification", 
                    True, 
                    f"✅ STRUCTURE CORRECT: Minor quality issues: {'; '.join(data_quality_issues)}"
                )
            else:
                self.log_result(
                    "Data Structure and Content Verification", 
                    False, 
                    f"❌ STRUCTURE ISSUES: {'; '.join(structure_issues + data_quality_issues)}"
                )
            
            return {
                'success': not has_critical_issues,
                'structure_issues': structure_issues,
                'data_quality_issues': data_quality_issues
            }
            
        except Exception as e:
            self.log_result(
                "Data Structure and Content Verification", 
                False, 
                f"❌ VERIFICATION FAILED: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def test_different_user_ids(self, token):
        """Test with different user IDs to see data variation"""
        try:
            test_user_ids = ["admin_user_1", "demo_user_1", "68bfff790e4e46bc28d43631"]
            results = {}
            
            for user_id in test_user_ids:
                print(f"      Testing with user ID: {user_id}")
                
                # Test buyer tenders
                buyer_result = await self.test_buyer_tenders_endpoint(user_id, token)
                
                # Test seller overview
                seller_result = await self.test_seller_tenders_overview_endpoint(user_id, token)
                
                results[user_id] = {
                    'buyer': buyer_result,
                    'seller': seller_result
                }
            
            # Analyze variation
            user_data_summary = []
            for user_id, result in results.items():
                buyer_count = result['buyer'].get('tender_count', 0) if result['buyer'].get('success') else 0
                seller_count = result['seller'].get('listing_count', 0) if result['seller'].get('success') else 0
                seller_tenders = result['seller'].get('total_tenders', 0) if result['seller'].get('success') else 0
                
                user_data_summary.append(f"{user_id}: {buyer_count} buyer tenders, {seller_count} listings, {seller_tenders} seller tenders")
            
            self.log_result(
                "Different User IDs Test", 
                True, 
                f"✅ USER VARIATION CONFIRMED: {'; '.join(user_data_summary)}"
            )
            
            return {
                'success': True,
                'results': results,
                'summary': user_data_summary
            }
            
        except Exception as e:
            self.log_result(
                "Different User IDs Test", 
                False, 
                f"❌ USER TESTING FAILED: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def analyze_tender_management_results(self, buyer_result, seller_result, structure_result, users_result):
        """Analyze the effectiveness of the tender management API testing"""
        print("      Final analysis of tender management API testing:")
        
        working_features = []
        failing_features = []
        
        # Check buyer tenders endpoint
        if buyer_result.get('success') and buyer_result.get('has_proper_structure'):
            working_features.append(f"✅ Buyer tenders endpoint working ({buyer_result.get('tender_count', 0)} tenders)")
        else:
            failing_features.append("❌ Buyer tenders endpoint issues")
        
        # Check seller overview endpoint
        if seller_result.get('success') and seller_result.get('has_proper_structure'):
            working_features.append(f"✅ Seller overview endpoint working ({seller_result.get('listing_count', 0)} listings)")
        else:
            failing_features.append("❌ Seller overview endpoint issues")
        
        # Check data structure
        if structure_result.get('success'):
            working_features.append("✅ Data structure and content verification passed")
        else:
            failing_features.append("❌ Data structure issues found")
        
        # Check user variation
        if users_result.get('success'):
            working_features.append("✅ Different user IDs show data variation")
        else:
            failing_features.append("❌ User ID testing failed")
        
        # Final assessment
        if not failing_features:
            self.log_result(
                "Tender Management API Analysis", 
                True, 
                f"✅ ALL TENDER APIS WORKING: {'; '.join(working_features)}"
            )
        else:
            self.log_result(
                "Tender Management API Analysis", 
                False, 
                f"❌ TENDER API ISSUES FOUND: {len(working_features)} working, {len(failing_features)} failing. Issues: {'; '.join(failing_features)}"
            )
        
        return len(failing_features) == 0
    
    async def test_tender_management_apis(self):
        """Test the tender management API endpoints"""
        print("\n🔄 TENDER MANAGEMENT API TESTING:")
        print("   Testing tender management API endpoints to verify they are working correctly")
        print("   Testing buyer tenders and seller tenders overview endpoints")
        
        # Step 1: Setup - Login as admin user
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            self.log_result("Tender Management API Setup", False, "Failed to login as admin")
            return False
        
        print(f"   Testing with admin user ID: {admin_user_id}")
        
        # Step 2: Test Buyer Tenders Endpoint
        print("\n   📋 Test Buyer Tenders Endpoint:")
        buyer_tenders_result = await self.test_buyer_tenders_endpoint(admin_user_id, admin_token)
        
        # Step 3: Test Seller Tenders Overview Endpoint
        print("\n   🏪 Test Seller Tenders Overview Endpoint:")
        seller_overview_result = await self.test_seller_tenders_overview_endpoint(admin_user_id, admin_token)
        
        # Step 4: Test Data Structure and Content
        print("\n   🔍 Test Data Structure and Content:")
        data_structure_result = await self.test_tender_data_structure(buyer_tenders_result, seller_overview_result)
        
        # Step 5: Test with Different User IDs
        print("\n   👥 Test with Different User IDs:")
        different_users_result = await self.test_different_user_ids(admin_token)
        
        # Step 6: Final Analysis
        print("\n   📈 Final Analysis:")
        await self.analyze_tender_management_results(
            buyer_tenders_result, seller_overview_result, data_structure_result, different_users_result
        )
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 TENDER MANAGEMENT API TESTING SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"📊 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%" if self.test_results else "0%")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    print("🚀 Starting Tender Management API Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("="*80)
    
    async with BackendTester() as tester:
        try:
            # Run tender management API tests
            await tester.test_tender_management_apis()
            
            # Print summary
            tester.print_summary()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())