#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - BUY TENDERS API PERFORMANCE INVESTIGATION
Testing performance comparison between Buy Tenders and Sell Tenders endpoints

SPECIFIC INVESTIGATION REQUESTED:
1. **Performance Comparison**: Time both endpoints and measure response times
   - GET /api/tenders/buyer/admin_user_1 (returns 14 items)
   - GET /api/tenders/seller/admin_user_1/overview (returns 62 items)

2. **Analyze Buy Tenders Response**: Check structure and seller enrichment
   - Verify seller enrichment is working correctly
   - Look for missing data that might cause processing delays
   - Check if all tenders have corresponding listings and sellers

3. **Database Query Analysis**: Check for slow database queries
   - Verify listing and seller lookups are efficient
   - Test for missing indexes or optimization opportunities

4. **Data Integrity Check**: Verify valid references
   - Check all buyer tenders have valid listing_id and seller_id references
   - Check for orphaned or invalid data causing processing delays
   - Confirm enrichment process is working correctly

5. **Compare API Optimization**: Compare optimization strategies
   - Check for inefficiencies in buyer tenders enrichment process

GOAL: Identify why Buy Tenders API (14 items) is slower than Sell Tenders API (62 items)
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
from datetime import datetime, timezone
import statistics

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://mobilefixed-market.preview.emergentagent.com/api"

class PerformanceTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.performance_data = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None, data_size=None):
        """Log test result with performance metrics"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "data_size": data_size,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        size_info = f" [{data_size} items]" if data_size else ""
        print(f"{status}: {test_name}{time_info}{size_info}")
        print(f"   Details: {details}")
        print()
    
    def log_performance(self, endpoint, response_time, data_size, data_structure):
        """Log performance data for analysis"""
        perf_data = {
            "endpoint": endpoint,
            "response_time": response_time,
            "data_size": data_size,
            "data_structure": data_structure,
            "timestamp": datetime.now().isoformat()
        }
        self.performance_data.append(perf_data)
    
    async def test_login_and_get_token(self, email="admin@cataloro.com", password="admin123"):
        """Test login and get JWT token"""
        start_time = time.time()
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            "Login Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id})",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Login Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response",
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
            response_time = (time.time() - start_time) * 1000
            self.log_result(
                "Login Authentication", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None, None, None
    
    async def measure_endpoint_performance(self, endpoint, headers, iterations=5):
        """Measure endpoint performance over multiple iterations"""
        response_times = []
        data_sizes = []
        last_response_data = None
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        data_size = len(data) if isinstance(data, list) else 1
                        
                        response_times.append(response_time)
                        data_sizes.append(data_size)
                        
                        if i == iterations - 1:  # Save last response for analysis
                            last_response_data = data
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f"HTTP {response.status}: {error_text}",
                            'response_time': response_time
                        }
                        
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                return {
                    'success': False,
                    'error': str(e),
                    'response_time': response_time
                }
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        median_response_time = statistics.median(response_times)
        avg_data_size = statistics.mean(data_sizes)
        
        return {
            'success': True,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'median_response_time': median_response_time,
            'avg_data_size': avg_data_size,
            'response_times': response_times,
            'data_sizes': data_sizes,
            'last_response_data': last_response_data
        }
    
    async def test_buy_tenders_performance(self, user_id, token):
        """Test Buy Tenders endpoint performance and analyze response structure"""
        print(f"      Testing Buy Tenders endpoint performance for user: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        endpoint = f"/tenders/buyer/{user_id}"
        
        # Measure performance over multiple iterations
        perf_result = await self.measure_endpoint_performance(endpoint, headers, iterations=5)
        
        if not perf_result['success']:
            self.log_result(
                "Buy Tenders Performance", 
                False, 
                f"❌ ENDPOINT FAILED: {perf_result['error']}",
                perf_result.get('response_time')
            )
            return perf_result
        
        # Analyze response structure
        data = perf_result['last_response_data']
        data_size = int(perf_result['avg_data_size'])
        avg_time = perf_result['avg_response_time']
        
        # Log performance data
        self.log_performance(endpoint, avg_time, data_size, self.analyze_data_structure(data))
        
        # Analyze data structure and enrichment
        structure_analysis = self.analyze_buy_tenders_structure(data)
        
        self.log_result(
            "Buy Tenders Performance", 
            True, 
            f"✅ PERFORMANCE MEASURED: Avg: {avg_time:.1f}ms, Min: {perf_result['min_response_time']:.1f}ms, Max: {perf_result['max_response_time']:.1f}ms, Data: {data_size} items",
            avg_time,
            data_size
        )
        
        return {
            **perf_result,
            'structure_analysis': structure_analysis,
            'endpoint': endpoint
        }
    
    async def test_sell_tenders_performance(self, user_id, token):
        """Test Sell Tenders Overview endpoint performance and analyze response structure"""
        print(f"      Testing Sell Tenders Overview endpoint performance for user: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        endpoint = f"/tenders/seller/{user_id}/overview"
        
        # Measure performance over multiple iterations
        perf_result = await self.measure_endpoint_performance(endpoint, headers, iterations=5)
        
        if not perf_result['success']:
            self.log_result(
                "Sell Tenders Performance", 
                False, 
                f"❌ ENDPOINT FAILED: {perf_result['error']}",
                perf_result.get('response_time')
            )
            return perf_result
        
        # Analyze response structure
        data = perf_result['last_response_data']
        data_size = int(perf_result['avg_data_size'])
        avg_time = perf_result['avg_response_time']
        
        # Log performance data
        self.log_performance(endpoint, avg_time, data_size, self.analyze_data_structure(data))
        
        # Analyze data structure and enrichment
        structure_analysis = self.analyze_sell_tenders_structure(data)
        
        self.log_result(
            "Sell Tenders Performance", 
            True, 
            f"✅ PERFORMANCE MEASURED: Avg: {avg_time:.1f}ms, Min: {perf_result['min_response_time']:.1f}ms, Max: {perf_result['max_response_time']:.1f}ms, Data: {data_size} items",
            avg_time,
            data_size
        )
        
        return {
            **perf_result,
            'structure_analysis': structure_analysis,
            'endpoint': endpoint
        }
    
    def analyze_data_structure(self, data):
        """Analyze the basic structure of response data"""
        if not isinstance(data, list):
            return {"type": type(data).__name__, "structure": "non-list"}
        
        if not data:
            return {"type": "list", "length": 0, "structure": "empty"}
        
        sample = data[0]
        return {
            "type": "list",
            "length": len(data),
            "sample_keys": list(sample.keys()) if isinstance(sample, dict) else [],
            "sample_key_count": len(sample.keys()) if isinstance(sample, dict) else 0
        }
    
    def analyze_buy_tenders_structure(self, data):
        """Analyze Buy Tenders response structure for performance issues"""
        if not isinstance(data, list) or not data:
            return {"error": "Invalid or empty data"}
        
        analysis = {
            "total_tenders": len(data),
            "enrichment_analysis": {},
            "data_integrity_issues": [],
            "performance_concerns": []
        }
        
        # Analyze enrichment completeness
        enrichment_fields = ['listing', 'seller']
        listing_subfields = ['id', 'title', 'price', 'images']
        seller_subfields = ['id', 'username', 'full_name']
        
        missing_enrichment = 0
        incomplete_listing_enrichment = 0
        incomplete_seller_enrichment = 0
        missing_references = 0
        
        for tender in data:
            # Check basic tender fields
            if not tender.get('listing_id') or not tender.get('seller_id'):
                missing_references += 1
                analysis["data_integrity_issues"].append(f"Tender {tender.get('id', 'unknown')} missing listing_id or seller_id")
            
            # Check listing enrichment
            listing = tender.get('listing', {})
            if not listing:
                missing_enrichment += 1
            else:
                missing_listing_fields = [field for field in listing_subfields if not listing.get(field)]
                if missing_listing_fields:
                    incomplete_listing_enrichment += 1
                    analysis["performance_concerns"].append(f"Incomplete listing enrichment: missing {missing_listing_fields}")
            
            # Check seller enrichment
            seller = tender.get('seller', {})
            if not seller:
                missing_enrichment += 1
            else:
                missing_seller_fields = [field for field in seller_subfields if not seller.get(field)]
                if missing_seller_fields:
                    incomplete_seller_enrichment += 1
                    analysis["performance_concerns"].append(f"Incomplete seller enrichment: missing {missing_seller_fields}")
        
        analysis["enrichment_analysis"] = {
            "missing_enrichment_count": missing_enrichment,
            "incomplete_listing_enrichment": incomplete_listing_enrichment,
            "incomplete_seller_enrichment": incomplete_seller_enrichment,
            "missing_references": missing_references,
            "enrichment_success_rate": ((len(data) - missing_enrichment) / len(data) * 100) if data else 0
        }
        
        # Performance concerns
        if missing_enrichment > 0:
            analysis["performance_concerns"].append(f"{missing_enrichment} tenders missing enrichment data")
        if missing_references > 0:
            analysis["performance_concerns"].append(f"{missing_references} tenders with invalid references")
        
        return analysis
    
    def analyze_sell_tenders_structure(self, data):
        """Analyze Sell Tenders Overview response structure"""
        if not isinstance(data, list) or not data:
            return {"error": "Invalid or empty data"}
        
        analysis = {
            "total_listings": len(data),
            "total_tenders": 0,
            "enrichment_analysis": {},
            "data_integrity_issues": [],
            "performance_concerns": []
        }
        
        # Count total tenders across all listings
        for listing_overview in data:
            tenders = listing_overview.get('tenders', [])
            analysis["total_tenders"] += len(tenders)
        
        # Analyze structure efficiency
        avg_tenders_per_listing = analysis["total_tenders"] / len(data) if data else 0
        analysis["enrichment_analysis"] = {
            "avg_tenders_per_listing": avg_tenders_per_listing,
            "structure_efficiency": "high" if avg_tenders_per_listing < 2 else "medium" if avg_tenders_per_listing < 5 else "low"
        }
        
        return analysis
    
    async def compare_performance_results(self, buy_result, sell_result):
        """Compare performance between Buy and Sell Tenders endpoints"""
        print("      Comparing performance results...")
        
        if not buy_result.get('success') or not sell_result.get('success'):
            self.log_result(
                "Performance Comparison", 
                False, 
                "❌ COMPARISON FAILED: One or both endpoints failed to respond"
            )
            return
        
        buy_time = buy_result['avg_response_time']
        sell_time = sell_result['avg_response_time']
        buy_size = int(buy_result['avg_data_size'])
        sell_size = int(sell_result['avg_data_size'])
        
        # Calculate performance metrics
        time_difference = buy_time - sell_time
        time_ratio = buy_time / sell_time if sell_time > 0 else float('inf')
        items_per_ms_buy = buy_size / buy_time if buy_time > 0 else 0
        items_per_ms_sell = sell_size / sell_time if sell_time > 0 else 0
        
        # Performance analysis
        performance_issues = []
        
        if time_difference > 100:  # More than 100ms slower
            performance_issues.append(f"Buy Tenders is {time_difference:.1f}ms slower than Sell Tenders")
        
        if time_ratio > 1.5:  # More than 50% slower
            performance_issues.append(f"Buy Tenders is {time_ratio:.1f}x slower despite having fewer items")
        
        if items_per_ms_buy < items_per_ms_sell * 0.5:  # Less than half the efficiency
            performance_issues.append(f"Buy Tenders efficiency: {items_per_ms_buy:.3f} items/ms vs Sell Tenders: {items_per_ms_sell:.3f} items/ms")
        
        # Analyze structural differences
        buy_structure = buy_result.get('structure_analysis', {})
        sell_structure = sell_result.get('structure_analysis', {})
        
        structural_issues = []
        
        # Check Buy Tenders enrichment issues
        buy_enrichment = buy_structure.get('enrichment_analysis', {})
        if buy_enrichment.get('missing_enrichment_count', 0) > 0:
            structural_issues.append(f"Buy Tenders: {buy_enrichment['missing_enrichment_count']} items missing enrichment")
        
        if buy_enrichment.get('enrichment_success_rate', 100) < 90:
            structural_issues.append(f"Buy Tenders: Low enrichment success rate ({buy_enrichment['enrichment_success_rate']:.1f}%)")
        
        # Root cause analysis
        root_causes = []
        
        if performance_issues:
            root_causes.append("PERFORMANCE ISSUE CONFIRMED: Buy Tenders API significantly slower than Sell Tenders API")
        
        if structural_issues:
            root_causes.append("ENRICHMENT ISSUES: Buy Tenders has data enrichment problems")
        
        if buy_enrichment.get('missing_references', 0) > 0:
            root_causes.append("DATA INTEGRITY ISSUES: Invalid listing_id or seller_id references causing lookup delays")
        
        # Final assessment
        if performance_issues or structural_issues:
            details = f"🔍 PERFORMANCE ISSUE IDENTIFIED: {'; '.join(performance_issues + structural_issues + root_causes)}"
            success = False
        else:
            details = f"✅ PERFORMANCE ACCEPTABLE: Buy: {buy_time:.1f}ms ({buy_size} items), Sell: {sell_time:.1f}ms ({sell_size} items)"
            success = True
        
        self.log_result(
            "Performance Comparison Analysis", 
            success, 
            details
        )
        
        return {
            'performance_issues': performance_issues,
            'structural_issues': structural_issues,
            'root_causes': root_causes,
            'buy_time': buy_time,
            'sell_time': sell_time,
            'buy_size': buy_size,
            'sell_size': sell_size,
            'time_difference': time_difference,
            'time_ratio': time_ratio
        }
    
    async def test_data_integrity(self, buy_result, token):
        """Test data integrity of Buy Tenders response"""
        print("      Testing data integrity of Buy Tenders response...")
        
        if not buy_result.get('success'):
            self.log_result(
                "Data Integrity Check", 
                False, 
                "❌ INTEGRITY CHECK SKIPPED: Buy Tenders endpoint failed"
            )
            return
        
        data = buy_result.get('last_response_data', [])
        if not data:
            self.log_result(
                "Data Integrity Check", 
                False, 
                "❌ NO DATA: Buy Tenders returned empty response"
            )
            return
        
        integrity_issues = []
        orphaned_data = []
        valid_references = 0
        
        # Check each tender for data integrity
        for i, tender in enumerate(data):
            tender_id = tender.get('id', f'tender_{i}')
            
            # Check required fields
            if not tender.get('listing_id'):
                integrity_issues.append(f"Tender {tender_id}: Missing listing_id")
            if not tender.get('seller_id'):
                integrity_issues.append(f"Tender {tender_id}: Missing seller_id")
            if not tender.get('buyer_id'):
                integrity_issues.append(f"Tender {tender_id}: Missing buyer_id")
            
            # Check enrichment data
            listing = tender.get('listing', {})
            seller = tender.get('seller', {})
            
            if not listing:
                orphaned_data.append(f"Tender {tender_id}: No listing enrichment data")
            elif not listing.get('id') or not listing.get('title'):
                orphaned_data.append(f"Tender {tender_id}: Incomplete listing data")
            
            if not seller:
                orphaned_data.append(f"Tender {tender_id}: No seller enrichment data")
            elif not seller.get('id') or not seller.get('username'):
                orphaned_data.append(f"Tender {tender_id}: Incomplete seller data")
            
            # Count valid references
            if (tender.get('listing_id') and tender.get('seller_id') and 
                listing.get('id') and seller.get('id')):
                valid_references += 1
        
        # Calculate integrity metrics
        total_tenders = len(data)
        integrity_rate = (valid_references / total_tenders * 100) if total_tenders > 0 else 0
        
        # Assessment
        if integrity_rate >= 95 and len(integrity_issues) == 0:
            self.log_result(
                "Data Integrity Check", 
                True, 
                f"✅ DATA INTEGRITY GOOD: {integrity_rate:.1f}% valid references ({valid_references}/{total_tenders})"
            )
        elif integrity_rate >= 80:
            self.log_result(
                "Data Integrity Check", 
                True, 
                f"⚠️ DATA INTEGRITY ACCEPTABLE: {integrity_rate:.1f}% valid references, {len(integrity_issues)} issues, {len(orphaned_data)} orphaned records"
            )
        else:
            self.log_result(
                "Data Integrity Check", 
                False, 
                f"❌ DATA INTEGRITY POOR: {integrity_rate:.1f}% valid references, {len(integrity_issues)} critical issues, {len(orphaned_data)} orphaned records"
            )
        
        return {
            'integrity_rate': integrity_rate,
            'valid_references': valid_references,
            'total_tenders': total_tenders,
            'integrity_issues': integrity_issues,
            'orphaned_data': orphaned_data
        }
    
    async def test_performance_investigation(self):
        """Main performance investigation test"""
        print("\n🔍 BUY TENDERS API PERFORMANCE INVESTIGATION:")
        print("   Investigating performance difference between Buy Tenders and Sell Tenders endpoints")
        print("   Goal: Identify why Buy Tenders (14 items) is slower than Sell Tenders (62 items)")
        
        # Step 1: Setup - Login as admin user
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            self.log_result("Performance Investigation Setup", False, "Failed to login as admin")
            return False
        
        print(f"   Testing with admin user ID: {admin_user_id}")
        
        # Step 2: Test Buy Tenders Performance
        print("\n   📊 Test Buy Tenders Performance:")
        buy_result = await self.test_buy_tenders_performance(admin_user_id, admin_token)
        
        # Step 3: Test Sell Tenders Performance
        print("\n   📊 Test Sell Tenders Performance:")
        sell_result = await self.test_sell_tenders_performance(admin_user_id, admin_token)
        
        # Step 4: Compare Performance
        print("\n   ⚖️ Compare Performance Results:")
        comparison_result = await self.compare_performance_results(buy_result, sell_result)
        
        # Step 5: Test Data Integrity
        print("\n   🔍 Test Data Integrity:")
        integrity_result = await self.test_data_integrity(buy_result, admin_token)
        
        # Step 6: Generate Performance Report
        print("\n   📋 Generate Performance Report:")
        await self.generate_performance_report(buy_result, sell_result, comparison_result, integrity_result)
        
        return True
    
    async def generate_performance_report(self, buy_result, sell_result, comparison_result, integrity_result):
        """Generate comprehensive performance analysis report"""
        
        report_sections = []
        
        # Performance Summary
        if buy_result.get('success') and sell_result.get('success'):
            buy_time = buy_result['avg_response_time']
            sell_time = sell_result['avg_response_time']
            buy_size = int(buy_result['avg_data_size'])
            sell_size = int(sell_result['avg_data_size'])
            
            report_sections.append(f"PERFORMANCE SUMMARY: Buy Tenders: {buy_time:.1f}ms ({buy_size} items), Sell Tenders: {sell_time:.1f}ms ({sell_size} items)")
        
        # Root Cause Analysis
        if comparison_result:
            root_causes = comparison_result.get('root_causes', [])
            if root_causes:
                report_sections.append(f"ROOT CAUSES IDENTIFIED: {'; '.join(root_causes)}")
        
        # Data Integrity Issues
        if integrity_result:
            integrity_rate = integrity_result.get('integrity_rate', 0)
            if integrity_rate < 95:
                report_sections.append(f"DATA INTEGRITY CONCERNS: {integrity_rate:.1f}% valid references, {len(integrity_result.get('integrity_issues', []))} issues")
        
        # Recommendations
        recommendations = []
        
        if comparison_result and comparison_result.get('time_ratio', 1) > 1.5:
            recommendations.append("OPTIMIZE Buy Tenders enrichment process")
        
        if integrity_result and integrity_result.get('integrity_rate', 100) < 90:
            recommendations.append("FIX data integrity issues with invalid references")
        
        if buy_result.get('structure_analysis', {}).get('enrichment_analysis', {}).get('missing_enrichment_count', 0) > 0:
            recommendations.append("IMPLEMENT database indexes for listing and seller lookups")
        
        if recommendations:
            report_sections.append(f"RECOMMENDATIONS: {'; '.join(recommendations)}")
        
        # Final Report
        report = f"🔍 PERFORMANCE INVESTIGATION COMPLETE: {'; '.join(report_sections)}"
        
        self.log_result(
            "Performance Investigation Report", 
            True, 
            report
        )
    
    def print_summary(self):
        """Print test summary with performance analysis"""
        print("\n" + "="*80)
        print("🎯 BUY TENDERS API PERFORMANCE INVESTIGATION SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"📊 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%" if self.test_results else "0%")
        
        # Performance Analysis Summary
        if self.performance_data:
            print(f"\n📊 PERFORMANCE ANALYSIS:")
            for perf in self.performance_data:
                endpoint = perf['endpoint'].split('/')[-1] if '/' in perf['endpoint'] else perf['endpoint']
                print(f"   • {endpoint}: {perf['response_time']:.1f}ms ({perf['data_size']} items)")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    print("🚀 Starting Buy Tenders API Performance Investigation...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("="*80)
    
    async with PerformanceTester() as tester:
        try:
            # Run performance investigation
            await tester.test_performance_investigation()
            
            # Print summary
            tester.print_summary()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())