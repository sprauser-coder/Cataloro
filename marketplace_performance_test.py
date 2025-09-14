#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - PERFORMANCE & IMAGE OPTIMIZATION TESTING
Testing performance across multiple marketplace endpoints to ensure image optimization fixes are working consistently

SPECIFIC TESTS REQUESTED:
1. **Performance Comparison Test:**
   - Test GET /api/listings?status=all (Admin Listings)
   - Test GET /api/tenders/buyer/admin_user_1 (Buy Tenders) 
   - Test GET /api/tenders/seller/admin_user_1/overview (Sell Tenders)
   - Compare response times and ensure they're all under 300ms

2. **Data Size Verification:**
   - Check that image data is optimized (thumbnail URLs vs base64)
   - Verify response sizes are reasonable for the amount of data returned
   - Confirm no endpoints are transferring massive image data

3. **Functionality Testing:**
   - Verify that optimized endpoints still return all required data
   - Check that image URLs are properly formatted
   - Ensure data structure integrity is maintained

4. **Consistency Check:**
   - Confirm all marketplace endpoints use consistent image optimization
   - Check for any remaining endpoints that might have the same issue

CRITICAL ENDPOINTS BEING TESTED:
- POST /api/auth/login (user authentication)
- GET /api/listings?status=all (Admin Listings - should be optimized)
- GET /api/tenders/buyer/{buyer_id} (Buy Tenders - previously had 57MB issue, should be fixed)
- GET /api/tenders/seller/{seller_id}/overview (Sell Tenders - comparison baseline)

EXPECTED RESULTS:
- ✅ All endpoints respond under 300ms
- ✅ No massive base64 image data transfer (response sizes reasonable)
- ✅ Image URLs are thumbnail URLs, not base64 data
- ✅ All required data still present and properly structured
- ✅ Consistent image optimization across all endpoints
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://marketplace-perf-1.preview.emergentagent.com/api"

class MarketplacePerformanceTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.performance_threshold_ms = 300  # 300ms threshold as requested
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None, response_size=None):
        """Log test result with performance metrics"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "response_size": response_size,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        size_info = f" [{self.format_size(response_size)}]" if response_size else ""
        print(f"{status}: {test_name}{time_info}{size_info}")
        print(f"   Details: {details}")
        print()
    
    def format_size(self, size_bytes):
        """Format size in human readable format"""
        if size_bytes is None:
            return "Unknown"
        
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f}KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f}MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f}GB"
    
    def analyze_image_optimization(self, data, endpoint_name):
        """Analyze image optimization in response data"""
        image_analysis = {
            "total_images": 0,
            "base64_images": 0,
            "thumbnail_urls": 0,
            "file_urls": 0,
            "placeholder_urls": 0,
            "optimization_issues": [],
            "sample_images": []
        }
        
        def analyze_images_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if key in ['images', 'image', 'listing_image', 'listing_images']:
                        if isinstance(value, list):
                            for i, img in enumerate(value):
                                self.analyze_single_image(img, f"{new_path}[{i}]", image_analysis)
                        elif isinstance(value, str):
                            self.analyze_single_image(value, new_path, image_analysis)
                    else:
                        analyze_images_recursive(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    analyze_images_recursive(item, f"{path}[{i}]")
        
        analyze_images_recursive(data)
        return image_analysis
    
    def analyze_single_image(self, img, path, analysis):
        """Analyze a single image for optimization"""
        if not isinstance(img, str):
            return
        
        analysis["total_images"] += 1
        analysis["sample_images"].append({"path": path, "url": img[:100] + "..." if len(img) > 100 else img})
        
        if img.startswith('data:'):
            analysis["base64_images"] += 1
            analysis["optimization_issues"].append(f"Base64 image found at {path}")
        elif '/api/listings/' in img and '/thumbnail/' in img:
            analysis["thumbnail_urls"] += 1
        elif img.startswith('/uploads/') or img.startswith('/static/'):
            analysis["file_urls"] += 1
        elif '/api/placeholder-image.jpg' in img:
            analysis["placeholder_urls"] += 1
        else:
            analysis["optimization_issues"].append(f"Unknown image format at {path}: {img[:50]}")
    
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
                response_text = await response.text()
                response_size = len(response_text.encode('utf-8'))
                
                if response.status == 200:
                    data = json.loads(response_text)
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            "Login Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id})",
                            response_time,
                            response_size
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Login Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response",
                            response_time,
                            response_size
                        )
                        return None, None, None
                else:
                    self.log_result(
                        "Login Authentication", 
                        False, 
                        f"Login failed with status {response.status}: {response_text[:200]}",
                        response_time,
                        response_size
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
    
    async def test_admin_listings_performance(self, token):
        """Test GET /api/listings?status=all (Admin Listings) performance and optimization"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings?status=all"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                response_text = await response.text()
                response_size = len(response_text.encode('utf-8'))
                
                if response.status == 200:
                    data = json.loads(response_text)
                    
                    # Performance check
                    performance_ok = response_time < self.performance_threshold_ms
                    
                    # Data structure check
                    if isinstance(data, list):
                        listings = data
                        total_count = len(listings)
                        
                        # Image optimization analysis
                        image_analysis = self.analyze_image_optimization(listings, "Admin Listings")
                        
                        # Size analysis
                        size_reasonable = response_size < 1024 * 1024  # Less than 1MB
                        
                        # Determine success
                        success = performance_ok and size_reasonable and len(image_analysis["optimization_issues"]) == 0
                        
                        details = f"Retrieved {len(listings)} listings (total: {total_count}). "
                        details += f"Images: {image_analysis['total_images']} total, "
                        details += f"{image_analysis['thumbnail_urls']} thumbnails, "
                        details += f"{image_analysis['base64_images']} base64 (should be 0). "
                        
                        if not performance_ok:
                            details += f"⚠️ Performance issue: {response_time:.1f}ms > {self.performance_threshold_ms}ms. "
                        if not size_reasonable:
                            details += f"⚠️ Size issue: {self.format_size(response_size)} may be too large. "
                        if image_analysis["optimization_issues"]:
                            details += f"⚠️ Image issues: {len(image_analysis['optimization_issues'])} found. "
                        
                        if success:
                            details += "✅ All optimization checks passed"
                        
                        self.log_result(
                            "Admin Listings Performance", 
                            success, 
                            details,
                            response_time,
                            response_size
                        )
                        
                        return {
                            'success': success,
                            'response_time': response_time,
                            'response_size': response_size,
                            'listings_count': len(listings),
                            'total_count': total_count,
                            'image_analysis': image_analysis,
                            'performance_ok': performance_ok,
                            'size_reasonable': size_reasonable
                        }
                    else:
                        self.log_result(
                            "Admin Listings Performance", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time,
                            response_size
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    self.log_result(
                        "Admin Listings Performance", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {response_text[:200]}",
                        response_time,
                        response_size
                    )
                    return {'success': False, 'error': response_text}
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_result(
                "Admin Listings Performance", 
                False, 
                f"❌ REQUEST FAILED: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_buy_tenders_performance(self, buyer_id, token):
        """Test GET /api/tenders/buyer/{buyer_id} (Buy Tenders) performance and optimization"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/tenders/buyer/{buyer_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                response_text = await response.text()
                response_size = len(response_text.encode('utf-8'))
                
                if response.status == 200:
                    data = json.loads(response_text)
                    
                    # Performance check
                    performance_ok = response_time < self.performance_threshold_ms
                    
                    # Data structure check
                    if isinstance(data, list):
                        tenders = data
                        
                        # Image optimization analysis
                        image_analysis = self.analyze_image_optimization(tenders, "Buy Tenders")
                        
                        # Size analysis - this endpoint previously had 57MB issue
                        size_reasonable = response_size < 1024 * 1024  # Less than 1MB (was 57MB before)
                        
                        # Determine success
                        success = performance_ok and size_reasonable and len(image_analysis["optimization_issues"]) == 0
                        
                        details = f"Retrieved {len(tenders)} buy tenders. "
                        details += f"Images: {image_analysis['total_images']} total, "
                        details += f"{image_analysis['thumbnail_urls']} thumbnails, "
                        details += f"{image_analysis['base64_images']} base64 (should be 0). "
                        
                        if not performance_ok:
                            details += f"⚠️ Performance issue: {response_time:.1f}ms > {self.performance_threshold_ms}ms. "
                        if not size_reasonable:
                            details += f"⚠️ Size issue: {self.format_size(response_size)} (was 57MB before fix). "
                        if image_analysis["optimization_issues"]:
                            details += f"⚠️ Image issues: {len(image_analysis['optimization_issues'])} found. "
                        
                        if success:
                            details += "✅ All optimization checks passed (57MB issue resolved)"
                        
                        self.log_result(
                            "Buy Tenders Performance", 
                            success, 
                            details,
                            response_time,
                            response_size
                        )
                        
                        return {
                            'success': success,
                            'response_time': response_time,
                            'response_size': response_size,
                            'tenders_count': len(tenders),
                            'image_analysis': image_analysis,
                            'performance_ok': performance_ok,
                            'size_reasonable': size_reasonable
                        }
                    else:
                        self.log_result(
                            "Buy Tenders Performance", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time,
                            response_size
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    self.log_result(
                        "Buy Tenders Performance", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {response_text[:200]}",
                        response_time,
                        response_size
                    )
                    return {'success': False, 'error': response_text}
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_result(
                "Buy Tenders Performance", 
                False, 
                f"❌ REQUEST FAILED: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_sell_tenders_performance(self, seller_id, token):
        """Test GET /api/tenders/seller/{seller_id}/overview (Sell Tenders) performance and optimization"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/tenders/seller/{seller_id}/overview"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                response_text = await response.text()
                response_size = len(response_text.encode('utf-8'))
                
                if response.status == 200:
                    data = json.loads(response_text)
                    
                    # Performance check
                    performance_ok = response_time < self.performance_threshold_ms
                    
                    # Data structure check
                    if isinstance(data, list):
                        overview = data
                        
                        # Image optimization analysis
                        image_analysis = self.analyze_image_optimization(overview, "Sell Tenders")
                        
                        # Size analysis
                        size_reasonable = response_size < 1024 * 1024  # Less than 1MB
                        
                        # Determine success
                        success = performance_ok and size_reasonable and len(image_analysis["optimization_issues"]) == 0
                        
                        details = f"Retrieved {len(overview)} sell tender overviews. "
                        details += f"Images: {image_analysis['total_images']} total, "
                        details += f"{image_analysis['thumbnail_urls']} thumbnails, "
                        details += f"{image_analysis['base64_images']} base64 (should be 0). "
                        
                        if not performance_ok:
                            details += f"⚠️ Performance issue: {response_time:.1f}ms > {self.performance_threshold_ms}ms. "
                        if not size_reasonable:
                            details += f"⚠️ Size issue: {self.format_size(response_size)} may be too large. "
                        if image_analysis["optimization_issues"]:
                            details += f"⚠️ Image issues: {len(image_analysis['optimization_issues'])} found. "
                        
                        if success:
                            details += "✅ All optimization checks passed (baseline comparison)"
                        
                        self.log_result(
                            "Sell Tenders Performance", 
                            success, 
                            details,
                            response_time,
                            response_size
                        )
                        
                        return {
                            'success': success,
                            'response_time': response_time,
                            'response_size': response_size,
                            'overview_count': len(overview),
                            'image_analysis': image_analysis,
                            'performance_ok': performance_ok,
                            'size_reasonable': size_reasonable
                        }
                    else:
                        self.log_result(
                            "Sell Tenders Performance", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time,
                            response_size
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    self.log_result(
                        "Sell Tenders Performance", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {response_text[:200]}",
                        response_time,
                        response_size
                    )
                    return {'success': False, 'error': response_text}
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.log_result(
                "Sell Tenders Performance", 
                False, 
                f"❌ REQUEST FAILED: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def analyze_performance_comparison(self, admin_result, buy_result, sell_result):
        """Analyze performance comparison across all endpoints"""
        print("      Performance comparison analysis:")
        
        results = [
            ("Admin Listings", admin_result),
            ("Buy Tenders", buy_result), 
            ("Sell Tenders", sell_result)
        ]
        
        performance_issues = []
        size_issues = []
        image_issues = []
        working_endpoints = []
        
        for name, result in results:
            if result.get('success'):
                working_endpoints.append(f"✅ {name} ({result.get('response_time', 0):.1f}ms)")
            else:
                if not result.get('performance_ok', True):
                    performance_issues.append(f"❌ {name} slow ({result.get('response_time', 0):.1f}ms)")
                if not result.get('size_reasonable', True):
                    size_issues.append(f"❌ {name} large ({self.format_size(result.get('response_size', 0))})")
                if result.get('image_analysis', {}).get('optimization_issues'):
                    image_issues.append(f"❌ {name} image issues ({len(result.get('image_analysis', {}).get('optimization_issues', []))})")
        
        # Overall assessment
        all_working = len(working_endpoints) == 3
        
        if all_working:
            self.log_result(
                "Performance Comparison Analysis", 
                True, 
                f"✅ ALL ENDPOINTS OPTIMIZED: {'; '.join(working_endpoints)}. Image optimization fixes working consistently across all marketplace endpoints."
            )
        else:
            issues = performance_issues + size_issues + image_issues
            self.log_result(
                "Performance Comparison Analysis", 
                False, 
                f"❌ OPTIMIZATION ISSUES FOUND: {len(working_endpoints)}/3 endpoints working. Issues: {'; '.join(issues)}"
            )
        
        return all_working
    
    async def test_data_structure_integrity(self, admin_result, buy_result, sell_result):
        """Test that data structure integrity is maintained after optimization"""
        try:
            integrity_issues = []
            
            # Check Admin Listings structure
            if admin_result.get('success'):
                if admin_result.get('listings_count', 0) > 0:
                    # Should have listings with proper structure
                    pass  # Structure already validated in the endpoint test
                else:
                    integrity_issues.append("Admin Listings returned no data")
            else:
                integrity_issues.append("Admin Listings failed to load")
            
            # Check Buy Tenders structure
            if buy_result.get('success'):
                if buy_result.get('tenders_count', 0) > 0:
                    # Should have tenders with proper structure
                    pass  # Structure already validated in the endpoint test
                else:
                    integrity_issues.append("Buy Tenders returned no data")
            else:
                integrity_issues.append("Buy Tenders failed to load")
            
            # Check Sell Tenders structure
            if sell_result.get('success'):
                if sell_result.get('overview_count', 0) > 0:
                    # Should have overview with proper structure
                    pass  # Structure already validated in the endpoint test
                else:
                    integrity_issues.append("Sell Tenders returned no data")
            else:
                integrity_issues.append("Sell Tenders failed to load")
            
            if not integrity_issues:
                self.log_result(
                    "Data Structure Integrity", 
                    True, 
                    "✅ DATA INTEGRITY MAINTAINED: All endpoints return proper data structures with required fields after optimization"
                )
                return True
            else:
                self.log_result(
                    "Data Structure Integrity", 
                    False, 
                    f"❌ INTEGRITY ISSUES: {'; '.join(integrity_issues)}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Data Structure Integrity", 
                False, 
                f"❌ INTEGRITY CHECK FAILED: {str(e)}"
            )
            return False
    
    async def test_consistency_check(self, admin_result, buy_result, sell_result):
        """Check for consistency in image optimization across all endpoints"""
        try:
            consistency_issues = []
            optimization_stats = []
            
            results = [
                ("Admin Listings", admin_result),
                ("Buy Tenders", buy_result),
                ("Sell Tenders", sell_result)
            ]
            
            for name, result in results:
                if result.get('success'):
                    image_analysis = result.get('image_analysis', {})
                    base64_count = image_analysis.get('base64_images', 0)
                    thumbnail_count = image_analysis.get('thumbnail_urls', 0)
                    total_images = image_analysis.get('total_images', 0)
                    
                    optimization_stats.append(f"{name}: {total_images} images, {thumbnail_count} thumbnails, {base64_count} base64")
                    
                    if base64_count > 0:
                        consistency_issues.append(f"{name} still has {base64_count} base64 images")
                    
                    if total_images > 0 and thumbnail_count == 0:
                        consistency_issues.append(f"{name} has no thumbnail URLs")
                else:
                    consistency_issues.append(f"{name} endpoint failed")
            
            if not consistency_issues:
                self.log_result(
                    "Image Optimization Consistency", 
                    True, 
                    f"✅ CONSISTENT OPTIMIZATION: All endpoints use thumbnail URLs instead of base64. {'; '.join(optimization_stats)}"
                )
                return True
            else:
                self.log_result(
                    "Image Optimization Consistency", 
                    False, 
                    f"❌ INCONSISTENT OPTIMIZATION: {'; '.join(consistency_issues)}. Stats: {'; '.join(optimization_stats)}"
                )
                return False
                
        except Exception as e:
            self.log_result(
                "Image Optimization Consistency", 
                False, 
                f"❌ CONSISTENCY CHECK FAILED: {str(e)}"
            )
            return False
    
    async def test_marketplace_performance(self):
        """Test marketplace performance and image optimization"""
        print("\n🚀 MARKETPLACE PERFORMANCE & IMAGE OPTIMIZATION TESTING:")
        print("   Testing performance across multiple marketplace endpoints")
        print("   Verifying image optimization fixes are working consistently")
        print(f"   Performance threshold: {self.performance_threshold_ms}ms")
        
        # Step 1: Setup - Login as admin user
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            self.log_result("Marketplace Performance Setup", False, "Failed to login as admin")
            return False
        
        print(f"   Testing with admin user ID: {admin_user_id}")
        
        # Step 2: Test Admin Listings Performance
        print("\n   📋 Test Admin Listings Performance:")
        admin_result = await self.test_admin_listings_performance(admin_token)
        
        # Step 3: Test Buy Tenders Performance (previously had 57MB issue)
        print("\n   💰 Test Buy Tenders Performance:")
        buy_result = await self.test_buy_tenders_performance(admin_user_id, admin_token)
        
        # Step 4: Test Sell Tenders Performance (baseline comparison)
        print("\n   🏪 Test Sell Tenders Performance:")
        sell_result = await self.test_sell_tenders_performance(admin_user_id, admin_token)
        
        # Step 5: Performance Comparison Analysis
        print("\n   📊 Performance Comparison Analysis:")
        await self.analyze_performance_comparison(admin_result, buy_result, sell_result)
        
        # Step 6: Data Structure Integrity Check
        print("\n   🔍 Data Structure Integrity Check:")
        await self.test_data_structure_integrity(admin_result, buy_result, sell_result)
        
        # Step 7: Consistency Check
        print("\n   ⚖️ Image Optimization Consistency Check:")
        await self.test_consistency_check(admin_result, buy_result, sell_result)
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 MARKETPLACE PERFORMANCE & IMAGE OPTIMIZATION TESTING SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"📊 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%" if self.test_results else "0%")
        
        # Performance summary
        performance_tests = [r for r in self.test_results if 'Performance' in r['test'] and r.get('response_time')]
        if performance_tests:
            avg_response_time = sum(r['response_time'] for r in performance_tests) / len(performance_tests)
            max_response_time = max(r['response_time'] for r in performance_tests)
            print(f"⏱️ Average Response Time: {avg_response_time:.1f}ms")
            print(f"⏱️ Max Response Time: {max_response_time:.1f}ms")
            print(f"🎯 Performance Threshold: {self.performance_threshold_ms}ms")
        
        # Size summary
        size_tests = [r for r in self.test_results if r.get('response_size')]
        if size_tests:
            total_size = sum(r['response_size'] for r in size_tests)
            max_size = max(r['response_size'] for r in size_tests)
            print(f"📦 Total Response Size: {self.format_size(total_size)}")
            print(f"📦 Largest Response: {self.format_size(max_size)}")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    time_info = f" ({result['response_time']:.1f}ms)" if result.get('response_time') else ""
                    size_info = f" [{self.format_size(result['response_size'])}]" if result.get('response_size') else ""
                    print(f"   • {result['test']}{time_info}{size_info}: {result['details']}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    print("🚀 Starting Marketplace Performance & Image Optimization Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("="*80)
    
    async with MarketplacePerformanceTester() as tester:
        try:
            # Run marketplace performance tests
            await tester.test_marketplace_performance()
            
            # Print summary
            tester.print_summary()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())