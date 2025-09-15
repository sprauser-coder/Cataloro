#!/usr/bin/env python3
"""
Cataloro Tenders API Testing Suite
Testing tenders endpoints for mobile/desktop consistency
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://self-hosted-shop.preview.emergentagent.com/api"

class TendersAPITester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.demo_user_id = "68bfff790e4e46bc28d43631"
        self.admin_user_id = "admin_user_1"
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
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
    
    async def test_buyer_tenders_endpoint(self, user_id: str, user_name: str) -> Dict:
        """Test GET /api/tenders/buyer/{user_id} endpoint"""
        print(f"🔍 Testing buyer tenders endpoint for {user_name} ({user_id})...")
        
        result = await self.make_request(f"/tenders/buyer/{user_id}")
        
        if result["success"]:
            tenders_data = result["data"]
            
            # Analyze data structure
            data_structure = self.analyze_buyer_tenders_structure(tenders_data)
            
            print(f"  ✅ Endpoint working: {len(tenders_data)} tenders found")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"  📊 Data structure: {data_structure['structure_score']:.1f}% complete")
            
            # Print sample data structure if available
            if tenders_data:
                print(f"  📋 Sample tender fields: {list(tenders_data[0].keys())}")
                if 'listing' in tenders_data[0]:
                    print(f"  📋 Sample listing fields: {list(tenders_data[0]['listing'].keys())}")
                if 'seller' in tenders_data[0]:
                    print(f"  📋 Sample seller fields: {list(tenders_data[0]['seller'].keys())}")
            
            return {
                "test_name": f"Buyer Tenders - {user_name}",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "tenders_count": len(tenders_data),
                "data_structure": data_structure,
                "sample_tender": tenders_data[0] if tenders_data else None,
                "user_id": user_id,
                "user_name": user_name
            }
        else:
            print(f"  ❌ Endpoint failed: {result.get('error', 'Unknown error')}")
            print(f"  📊 Status code: {result['status']}")
            return {
                "test_name": f"Buyer Tenders - {user_name}",
                "endpoint_working": False,
                "error": result.get("error", "Endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"],
                "user_id": user_id,
                "user_name": user_name
            }
    
    async def test_seller_tenders_overview_endpoint(self, user_id: str, user_name: str) -> Dict:
        """Test GET /api/tenders/seller/{user_id}/overview endpoint"""
        print(f"🔍 Testing seller tenders overview endpoint for {user_name} ({user_id})...")
        
        result = await self.make_request(f"/tenders/seller/{user_id}/overview")
        
        if result["success"]:
            overview_data = result["data"]
            
            # Analyze data structure
            data_structure = self.analyze_seller_overview_structure(overview_data)
            
            print(f"  ✅ Endpoint working: {len(overview_data)} listings with tenders")
            print(f"  ⏱️ Response time: {result['response_time_ms']:.0f}ms")
            print(f"  📊 Data structure: {data_structure['structure_score']:.1f}% complete")
            
            # Print sample data structure if available
            if overview_data:
                print(f"  📋 Sample overview fields: {list(overview_data[0].keys())}")
                if 'listing' in overview_data[0]:
                    print(f"  📋 Sample listing fields: {list(overview_data[0]['listing'].keys())}")
                if 'seller' in overview_data[0]:
                    print(f"  📋 Sample seller fields: {list(overview_data[0]['seller'].keys())}")
                if 'tenders' in overview_data[0] and overview_data[0]['tenders']:
                    print(f"  📋 Sample tender fields: {list(overview_data[0]['tenders'][0].keys())}")
            
            return {
                "test_name": f"Seller Overview - {user_name}",
                "endpoint_working": True,
                "response_time_ms": result["response_time_ms"],
                "listings_count": len(overview_data),
                "data_structure": data_structure,
                "sample_listing": overview_data[0] if overview_data else None,
                "user_id": user_id,
                "user_name": user_name
            }
        else:
            print(f"  ❌ Endpoint failed: {result.get('error', 'Unknown error')}")
            print(f"  📊 Status code: {result['status']}")
            return {
                "test_name": f"Seller Overview - {user_name}",
                "endpoint_working": False,
                "error": result.get("error", "Endpoint failed"),
                "response_time_ms": result["response_time_ms"],
                "status": result["status"],
                "user_id": user_id,
                "user_name": user_name
            }
    
    def analyze_buyer_tenders_structure(self, tenders_data: List[Dict]) -> Dict:
        """Analyze the data structure of buyer tenders response"""
        if not tenders_data:
            return {
                "structure_score": 100.0,
                "missing_fields": [],
                "field_analysis": {},
                "mobile_compatibility": True,
                "notes": "Empty response - valid structure"
            }
        
        # Expected fields for buyer tenders
        expected_fields = {
            "id": "string",
            "offer_amount": "number", 
            "status": "string",
            "created_at": "string",
            "listing": "object",
            "seller": "object"
        }
        
        expected_listing_fields = {
            "id": "string",
            "title": "string",
            "price": "number",
            "images": "array",
            "seller_id": "string"
        }
        
        expected_seller_fields = {
            "id": "string",
            "username": "string",
            "full_name": "string",
            "email": "string",
            "is_business": "boolean",
            "business_name": "string",
            "created_at": "string"
        }
        
        total_checks = 0
        passed_checks = 0
        missing_fields = []
        field_analysis = {}
        
        # Analyze first tender for structure
        sample_tender = tenders_data[0]
        
        # Check main tender fields
        for field, expected_type in expected_fields.items():
            total_checks += 1
            if field in sample_tender:
                passed_checks += 1
                field_analysis[field] = {
                    "present": True,
                    "type": type(sample_tender[field]).__name__,
                    "expected_type": expected_type,
                    "value": sample_tender[field] if field != "listing" and field != "seller" else "object"
                }
            else:
                missing_fields.append(f"tender.{field}")
                field_analysis[field] = {
                    "present": False,
                    "expected_type": expected_type
                }
        
        # Check listing object fields
        if "listing" in sample_tender and isinstance(sample_tender["listing"], dict):
            listing = sample_tender["listing"]
            for field, expected_type in expected_listing_fields.items():
                total_checks += 1
                if field in listing:
                    passed_checks += 1
                    field_analysis[f"listing.{field}"] = {
                        "present": True,
                        "type": type(listing[field]).__name__,
                        "expected_type": expected_type,
                        "value": listing[field] if field != "images" else f"array[{len(listing[field])}]"
                    }
                else:
                    missing_fields.append(f"listing.{field}")
                    field_analysis[f"listing.{field}"] = {
                        "present": False,
                        "expected_type": expected_type
                    }
        
        # Check seller object fields
        if "seller" in sample_tender and isinstance(sample_tender["seller"], dict):
            seller = sample_tender["seller"]
            for field, expected_type in expected_seller_fields.items():
                total_checks += 1
                if field in seller:
                    passed_checks += 1
                    field_analysis[f"seller.{field}"] = {
                        "present": True,
                        "type": type(seller[field]).__name__,
                        "expected_type": expected_type,
                        "value": seller[field]
                    }
                else:
                    missing_fields.append(f"seller.{field}")
                    field_analysis[f"seller.{field}"] = {
                        "present": False,
                        "expected_type": expected_type
                    }
        
        structure_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        mobile_compatibility = structure_score >= 80  # 80% or higher is mobile compatible
        
        return {
            "structure_score": structure_score,
            "missing_fields": missing_fields,
            "field_analysis": field_analysis,
            "mobile_compatibility": mobile_compatibility,
            "total_fields_checked": total_checks,
            "fields_present": passed_checks,
            "notes": f"Analyzed {len(tenders_data)} tenders"
        }
    
    def analyze_seller_overview_structure(self, overview_data: List[Dict]) -> Dict:
        """Analyze the data structure of seller overview response"""
        if not overview_data:
            return {
                "structure_score": 100.0,
                "missing_fields": [],
                "field_analysis": {},
                "mobile_compatibility": True,
                "notes": "Empty response - valid structure"
            }
        
        # Expected fields for seller overview
        expected_fields = {
            "listing": "object",
            "seller": "object", 
            "tender_count": "number",
            "highest_offer": "number",
            "tenders": "array"
        }
        
        expected_listing_fields = {
            "id": "string",
            "title": "string",
            "price": "number",
            "images": "array",
            "seller_id": "string"
        }
        
        expected_seller_fields = {
            "id": "string",
            "username": "string",
            "full_name": "string",
            "is_business": "boolean",
            "business_name": "string"
        }
        
        expected_tender_fields = {
            "id": "string",
            "offer_amount": "number",
            "created_at": "string",
            "buyer": "object"
        }
        
        expected_buyer_fields = {
            "id": "string",
            "username": "string",
            "full_name": "string",
            "is_business": "boolean",
            "business_name": "string"
        }
        
        total_checks = 0
        passed_checks = 0
        missing_fields = []
        field_analysis = {}
        
        # Analyze first overview item for structure
        sample_overview = overview_data[0]
        
        # Check main overview fields
        for field, expected_type in expected_fields.items():
            total_checks += 1
            if field in sample_overview:
                passed_checks += 1
                field_analysis[field] = {
                    "present": True,
                    "type": type(sample_overview[field]).__name__,
                    "expected_type": expected_type,
                    "value": sample_overview[field] if field not in ["listing", "seller", "tenders"] else f"{expected_type}"
                }
            else:
                missing_fields.append(f"overview.{field}")
                field_analysis[field] = {
                    "present": False,
                    "expected_type": expected_type
                }
        
        # Check listing object fields
        if "listing" in sample_overview and isinstance(sample_overview["listing"], dict):
            listing = sample_overview["listing"]
            for field, expected_type in expected_listing_fields.items():
                total_checks += 1
                if field in listing:
                    passed_checks += 1
                    field_analysis[f"listing.{field}"] = {
                        "present": True,
                        "type": type(listing[field]).__name__,
                        "expected_type": expected_type,
                        "value": listing[field] if field != "images" else f"array[{len(listing[field])}]"
                    }
                else:
                    missing_fields.append(f"listing.{field}")
                    field_analysis[f"listing.{field}"] = {
                        "present": False,
                        "expected_type": expected_type
                    }
        
        # Check seller object fields
        if "seller" in sample_overview and isinstance(sample_overview["seller"], dict):
            seller = sample_overview["seller"]
            for field, expected_type in expected_seller_fields.items():
                total_checks += 1
                if field in seller:
                    passed_checks += 1
                    field_analysis[f"seller.{field}"] = {
                        "present": True,
                        "type": type(seller[field]).__name__,
                        "expected_type": expected_type,
                        "value": seller[field]
                    }
                else:
                    missing_fields.append(f"seller.{field}")
                    field_analysis[f"seller.{field}"] = {
                        "present": False,
                        "expected_type": expected_type
                    }
        
        # Check tenders array structure
        if "tenders" in sample_overview and isinstance(sample_overview["tenders"], list) and sample_overview["tenders"]:
            sample_tender = sample_overview["tenders"][0]
            for field, expected_type in expected_tender_fields.items():
                total_checks += 1
                if field in sample_tender:
                    passed_checks += 1
                    field_analysis[f"tender.{field}"] = {
                        "present": True,
                        "type": type(sample_tender[field]).__name__,
                        "expected_type": expected_type,
                        "value": sample_tender[field] if field != "buyer" else "object"
                    }
                else:
                    missing_fields.append(f"tender.{field}")
                    field_analysis[f"tender.{field}"] = {
                        "present": False,
                        "expected_type": expected_type
                    }
            
            # Check buyer object in tender
            if "buyer" in sample_tender and isinstance(sample_tender["buyer"], dict):
                buyer = sample_tender["buyer"]
                for field, expected_type in expected_buyer_fields.items():
                    total_checks += 1
                    if field in buyer:
                        passed_checks += 1
                        field_analysis[f"buyer.{field}"] = {
                            "present": True,
                            "type": type(buyer[field]).__name__,
                            "expected_type": expected_type,
                            "value": buyer[field]
                        }
                    else:
                        missing_fields.append(f"buyer.{field}")
                        field_analysis[f"buyer.{field}"] = {
                            "present": False,
                            "expected_type": expected_type
                        }
        
        structure_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        mobile_compatibility = structure_score >= 80  # 80% or higher is mobile compatible
        
        return {
            "structure_score": structure_score,
            "missing_fields": missing_fields,
            "field_analysis": field_analysis,
            "mobile_compatibility": mobile_compatibility,
            "total_fields_checked": total_checks,
            "fields_present": passed_checks,
            "notes": f"Analyzed {len(overview_data)} listings with tenders"
        }
    
    async def test_data_consistency(self) -> Dict:
        """Test data consistency between mobile and desktop expectations"""
        print("🔄 Testing data consistency for mobile/desktop compatibility...")
        
        # Test both demo and admin users
        demo_buyer_result = await self.test_buyer_tenders_endpoint(self.demo_user_id, "Demo User")
        admin_buyer_result = await self.test_buyer_tenders_endpoint(self.admin_user_id, "Admin User")
        
        demo_seller_result = await self.test_seller_tenders_overview_endpoint(self.demo_user_id, "Demo User")
        admin_seller_result = await self.test_seller_tenders_overview_endpoint(self.admin_user_id, "Admin User")
        
        # Analyze consistency
        consistency_issues = []
        mobile_compatibility_issues = []
        
        # Check buyer endpoints consistency
        if demo_buyer_result["endpoint_working"] and admin_buyer_result["endpoint_working"]:
            demo_structure = demo_buyer_result["data_structure"]
            admin_structure = admin_buyer_result["data_structure"]
            
            if abs(demo_structure["structure_score"] - admin_structure["structure_score"]) > 5:  # Allow 5% variance
                consistency_issues.append("Buyer endpoints return different data structures between users")
            
            if not demo_structure["mobile_compatibility"]:
                mobile_compatibility_issues.append("Demo user buyer endpoint not mobile compatible")
            if not admin_structure["mobile_compatibility"]:
                mobile_compatibility_issues.append("Admin user buyer endpoint not mobile compatible")
        
        # Check seller endpoints consistency
        if demo_seller_result["endpoint_working"] and admin_seller_result["endpoint_working"]:
            demo_structure = demo_seller_result["data_structure"]
            admin_structure = admin_seller_result["data_structure"]
            
            if abs(demo_structure["structure_score"] - admin_structure["structure_score"]) > 5:  # Allow 5% variance
                consistency_issues.append("Seller endpoints return different data structures between users")
            
            if not demo_structure["mobile_compatibility"]:
                mobile_compatibility_issues.append("Demo user seller endpoint not mobile compatible")
            if not admin_structure["mobile_compatibility"]:
                mobile_compatibility_issues.append("Admin user seller endpoint not mobile compatible")
        
        return {
            "test_name": "Data Consistency Analysis",
            "consistency_issues": consistency_issues,
            "mobile_compatibility_issues": mobile_compatibility_issues,
            "data_consistent": len(consistency_issues) == 0,
            "mobile_compatible": len(mobile_compatibility_issues) == 0,
            "demo_buyer": demo_buyer_result,
            "admin_buyer": admin_buyer_result,
            "demo_seller": demo_seller_result,
            "admin_seller": admin_seller_result
        }
    
    def print_detailed_analysis(self, results: Dict):
        """Print detailed analysis of the test results"""
        print("\n" + "=" * 80)
        print("📋 DETAILED DATA STRUCTURE ANALYSIS")
        print("=" * 80)
        
        # Analyze Demo User Buyer Tenders
        demo_buyer = results.get("demo_user_buyer_tenders", {})
        if demo_buyer.get("endpoint_working"):
            print(f"\n🔍 Demo User Buyer Tenders ({demo_buyer.get('tenders_count', 0)} tenders):")
            data_structure = demo_buyer.get("data_structure", {})
            field_analysis = data_structure.get("field_analysis", {})
            
            for field, analysis in field_analysis.items():
                status = "✅" if analysis.get("present") else "❌"
                value = analysis.get("value", "N/A")
                print(f"  {status} {field}: {value}")
            
            missing = data_structure.get("missing_fields", [])
            if missing:
                print(f"  ⚠️ Missing fields: {', '.join(missing)}")
        
        # Analyze Admin User Buyer Tenders
        admin_buyer = results.get("admin_user_buyer_tenders", {})
        if admin_buyer.get("endpoint_working"):
            print(f"\n🔍 Admin User Buyer Tenders ({admin_buyer.get('tenders_count', 0)} tenders):")
            data_structure = admin_buyer.get("data_structure", {})
            field_analysis = data_structure.get("field_analysis", {})
            
            for field, analysis in field_analysis.items():
                status = "✅" if analysis.get("present") else "❌"
                value = analysis.get("value", "N/A")
                print(f"  {status} {field}: {value}")
            
            missing = data_structure.get("missing_fields", [])
            if missing:
                print(f"  ⚠️ Missing fields: {', '.join(missing)}")
        
        # Analyze Demo User Seller Overview
        demo_seller = results.get("demo_user_seller_overview", {})
        if demo_seller.get("endpoint_working"):
            print(f"\n🔍 Demo User Seller Overview ({demo_seller.get('listings_count', 0)} listings):")
            data_structure = demo_seller.get("data_structure", {})
            field_analysis = data_structure.get("field_analysis", {})
            
            for field, analysis in field_analysis.items():
                status = "✅" if analysis.get("present") else "❌"
                value = analysis.get("value", "N/A")
                print(f"  {status} {field}: {value}")
            
            missing = data_structure.get("missing_fields", [])
            if missing:
                print(f"  ⚠️ Missing fields: {', '.join(missing)}")
        
        # Analyze Admin User Seller Overview
        admin_seller = results.get("admin_user_seller_overview", {})
        if admin_seller.get("endpoint_working"):
            print(f"\n🔍 Admin User Seller Overview ({admin_seller.get('listings_count', 0)} listings):")
            data_structure = admin_seller.get("data_structure", {})
            field_analysis = data_structure.get("field_analysis", {})
            
            for field, analysis in field_analysis.items():
                status = "✅" if analysis.get("present") else "❌"
                value = analysis.get("value", "N/A")
                print(f"  {status} {field}: {value}")
            
            missing = data_structure.get("missing_fields", [])
            if missing:
                print(f"  ⚠️ Missing fields: {', '.join(missing)}")
    
    async def run_comprehensive_tenders_test(self) -> Dict:
        """Run comprehensive tenders API testing"""
        print("🚀 Starting Cataloro Tenders API Testing")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Test individual endpoints
            demo_buyer = await self.test_buyer_tenders_endpoint(self.demo_user_id, "Demo User")
            admin_buyer = await self.test_buyer_tenders_endpoint(self.admin_user_id, "Admin User")
            
            demo_seller = await self.test_seller_tenders_overview_endpoint(self.demo_user_id, "Demo User")
            admin_seller = await self.test_seller_tenders_overview_endpoint(self.admin_user_id, "Admin User")
            
            # Test data consistency
            consistency = await self.test_data_consistency()
            
            # Compile results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "demo_user_buyer_tenders": demo_buyer,
                "admin_user_buyer_tenders": admin_buyer,
                "demo_user_seller_overview": demo_seller,
                "admin_user_seller_overview": admin_seller,
                "data_consistency": consistency
            }
            
            # Calculate success metrics
            endpoint_tests = [demo_buyer, admin_buyer, demo_seller, admin_seller]
            working_endpoints = [t for t in endpoint_tests if t.get("endpoint_working", False)]
            
            mobile_compatible_endpoints = [
                t for t in endpoint_tests 
                if t.get("endpoint_working", False) and 
                t.get("data_structure", {}).get("mobile_compatibility", False)
            ]
            
            all_results["summary"] = {
                "total_endpoints_tested": len(endpoint_tests),
                "working_endpoints": len(working_endpoints),
                "endpoint_success_rate": len(working_endpoints) / len(endpoint_tests) * 100,
                "mobile_compatible_endpoints": len(mobile_compatible_endpoints),
                "mobile_compatibility_rate": len(mobile_compatible_endpoints) / len(endpoint_tests) * 100,
                "data_consistency_verified": consistency.get("data_consistent", False),
                "mobile_compatibility_verified": consistency.get("mobile_compatible", False),
                "all_endpoints_working": len(working_endpoints) == len(endpoint_tests),
                "all_mobile_compatible": len(mobile_compatible_endpoints) == len(endpoint_tests),
                "demo_user_has_tenders": demo_buyer.get("tenders_count", 0) > 0 or demo_seller.get("listings_count", 0) > 0,
                "admin_user_has_tenders": admin_buyer.get("tenders_count", 0) > 0 or admin_seller.get("listings_count", 0) > 0
            }
            
            # Print detailed analysis
            self.print_detailed_analysis(all_results)
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Run tenders API tests"""
    print("🚀 Starting Cataloro Tenders API Testing Suite")
    print("=" * 60)
    
    # Run Tenders API Tests
    tenders_tester = TendersAPITester()
    tenders_results = await tenders_tester.run_comprehensive_tenders_test()
    
    print("\n" + "=" * 60)
    print("📊 TENDERS API TEST RESULTS SUMMARY")
    print("=" * 60)
    
    # Print tenders summary
    tenders_summary = tenders_results.get("summary", {})
    print(f"Endpoint Success Rate: {tenders_summary.get('endpoint_success_rate', 0):.1f}%")
    print(f"Mobile Compatibility Rate: {tenders_summary.get('mobile_compatibility_rate', 0):.1f}%")
    print(f"Data Consistency: {'✅' if tenders_summary.get('data_consistency_verified') else '❌'}")
    print(f"Mobile Compatibility: {'✅' if tenders_summary.get('mobile_compatibility_verified') else '❌'}")
    print(f"Demo User Has Tenders: {'✅' if tenders_summary.get('demo_user_has_tenders') else '❌'}")
    print(f"Admin User Has Tenders: {'✅' if tenders_summary.get('admin_user_has_tenders') else '❌'}")
    print(f"All Endpoints Working: {'✅' if tenders_summary.get('all_endpoints_working') else '❌'}")
    print(f"All Mobile Compatible: {'✅' if tenders_summary.get('all_mobile_compatible') else '❌'}")
    
    print("\n" + "=" * 60)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    # Determine overall status
    if tenders_summary.get('all_endpoints_working') and tenders_summary.get('all_mobile_compatible'):
        print("🎉 ALL TENDERS ENDPOINTS WORKING AND MOBILE COMPATIBLE")
        status = "EXCELLENT"
    elif tenders_summary.get('endpoint_success_rate', 0) >= 75:
        print("✅ TENDERS ENDPOINTS MOSTLY FUNCTIONAL")
        status = "GOOD"
    elif tenders_summary.get('endpoint_success_rate', 0) >= 50:
        print("⚠️ TENDERS ENDPOINTS PARTIALLY FUNCTIONAL - NEEDS ATTENTION")
        status = "NEEDS_ATTENTION"
    else:
        print("❌ CRITICAL TENDERS API ISSUES DETECTED")
        status = "CRITICAL"
    
    # Print recommendations
    print("\n📋 RECOMMENDATIONS:")
    
    consistency = tenders_results.get("data_consistency", {})
    if consistency.get("consistency_issues"):
        print("⚠️ Data consistency issues found:")
        for issue in consistency["consistency_issues"]:
            print(f"   - {issue}")
    
    if consistency.get("mobile_compatibility_issues"):
        print("⚠️ Mobile compatibility issues found:")
        for issue in consistency["mobile_compatibility_issues"]:
            print(f"   - {issue}")
    
    if not tenders_summary.get('demo_user_has_tenders') and not tenders_summary.get('admin_user_has_tenders'):
        print("ℹ️ No tenders found for either user - this may be expected if no bids have been placed")
    
    return {
        "tenders_results": tenders_results,
        "overall_status": status,
        "success_rate": tenders_summary.get('endpoint_success_rate', 0)
    }


if __name__ == "__main__":
    asyncio.run(main())