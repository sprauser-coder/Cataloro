#!/usr/bin/env python3
"""
AI-Powered Search Endpoints Testing for Cataloro Marketplace
Testing the new AI-enhanced search functionality and recommendations
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"

class AISearchTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = None
        self.test_listings = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": "✅ PASSED" if status else "❌ FAILED",
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{result['status']} - {test_name}: {details}")
        
    async def create_test_user(self):
        """Create a test user for personalized recommendations"""
        try:
            user_data = {
                "username": "ai_test_user",
                "email": "ai_test@cataloro.com",
                "full_name": "AI Test User",
                "password": "testpass123"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/register", json=user_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.test_user_id = result.get("user_id")
                    self.log_test("Create Test User", True, f"User ID: {self.test_user_id}")
                    return True
                else:
                    # User might already exist, try login
                    async with self.session.post(f"{BACKEND_URL}/auth/login", json={"email": user_data["email"]}) as login_response:
                        if login_response.status == 200:
                            login_result = await login_response.json()
                            self.test_user_id = login_result.get("user", {}).get("id")
                            self.log_test("Login Test User", True, f"User ID: {self.test_user_id}")
                            return True
                        else:
                            self.log_test("Create/Login Test User", False, f"Status: {login_response.status}")
                            return False
        except Exception as e:
            self.log_test("Create Test User", False, f"Error: {str(e)}")
            return False
            
    async def create_test_listings(self):
        """Create diverse test listings for AI search testing"""
        test_listings_data = [
            {
                "title": "Gaming Laptop - High Performance",
                "description": "Powerful gaming laptop with RTX 4070, 16GB RAM, perfect for gaming and streaming",
                "price": 1299.99,
                "category": "Electronics",
                "condition": "new",
                "seller_id": self.test_user_id,
                "tags": ["gaming", "laptop", "RTX", "high-performance"],
                "features": ["16GB RAM", "RTX 4070", "1TB SSD"]
            },
            {
                "title": "Wireless Noise-Cancelling Headphones",
                "description": "Premium wireless headphones with active noise cancellation, 30-hour battery life",
                "price": 299.99,
                "category": "Electronics",
                "condition": "new",
                "seller_id": self.test_user_id,
                "tags": ["wireless", "headphones", "noise-cancelling", "premium"],
                "features": ["30h battery", "ANC", "Bluetooth 5.0"]
            },
            {
                "title": "Vintage Electric Guitar - Fender Style",
                "description": "Beautiful vintage-style electric guitar, perfect for blues and rock music",
                "price": 599.99,
                "category": "Musical Instruments",
                "condition": "used",
                "seller_id": self.test_user_id,
                "tags": ["guitar", "vintage", "electric", "fender"],
                "features": ["Maple neck", "Humbucker pickups", "Vintage finish"]
            },
            {
                "title": "Professional Camera Lens 50mm",
                "description": "High-quality 50mm prime lens for professional photography",
                "price": 899.99,
                "category": "Photography",
                "condition": "new",
                "seller_id": self.test_user_id,
                "tags": ["camera", "lens", "50mm", "professional"],
                "features": ["f/1.4 aperture", "Weather sealed", "Image stabilization"]
            },
            {
                "title": "Budget Smartphone - Great Value",
                "description": "Affordable smartphone with good camera and long battery life",
                "price": 199.99,
                "category": "Electronics",
                "condition": "new",
                "seller_id": self.test_user_id,
                "tags": ["smartphone", "budget", "affordable", "camera"],
                "features": ["48MP camera", "5000mAh battery", "128GB storage"]
            }
        ]
        
        created_count = 0
        for listing_data in test_listings_data:
            try:
                async with self.session.post(f"{BACKEND_URL}/listings", json=listing_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.test_listings.append(result.get("listing_id"))
                        created_count += 1
                    else:
                        print(f"Failed to create listing: {listing_data['title']} - Status: {response.status}")
            except Exception as e:
                print(f"Error creating listing {listing_data['title']}: {str(e)}")
                
        self.log_test("Create Test Listings", created_count > 0, f"Created {created_count}/5 listings")
        return created_count > 0
        
    async def test_ai_search_suggestions(self):
        """Test AI-powered search suggestions endpoint"""
        test_queries = [
            "gaming laptop",
            "wireless headphones", 
            "vintage guitar",
            "camera lens",
            "budget phone"
        ]
        
        passed_tests = 0
        total_tests = len(test_queries)
        
        for query in test_queries:
            try:
                search_data = {
                    "query": query,
                    "context": {
                        "previous_searches": ["electronics", "gaming"]
                    }
                }
                
                async with self.session.post(f"{BACKEND_URL}/search/ai-suggestions", json=search_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        suggestions = result.get("suggestions", [])
                        
                        if isinstance(suggestions, list) and len(suggestions) <= 5:
                            passed_tests += 1
                            self.log_test(f"AI Suggestions for '{query}'", True, f"Got {len(suggestions)} suggestions: {suggestions[:2]}")
                        else:
                            self.log_test(f"AI Suggestions for '{query}'", False, f"Invalid suggestions format: {suggestions}")
                    else:
                        self.log_test(f"AI Suggestions for '{query}'", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(f"AI Suggestions for '{query}'", False, f"Error: {str(e)}")
                
        overall_success = passed_tests >= (total_tests * 0.8)  # 80% success rate
        self.log_test("AI Search Suggestions Overall", overall_success, f"{passed_tests}/{total_tests} queries successful")
        return overall_success
        
    async def test_intelligent_search(self):
        """Test AI-enhanced intelligent search endpoint"""
        test_cases = [
            {
                "query": "gaming laptop under 1500",
                "filters": {},
                "expected_features": ["enhanced_query", "results"]
            },
            {
                "query": "wireless headphones",
                "filters": {"category": "Electronics", "min_price": 200},
                "expected_features": ["results", "total"]
            },
            {
                "query": "vintage guitar",
                "filters": {"condition": "used"},
                "expected_features": ["search_intent", "applied_filters"]
            },
            {
                "query": "budget smartphone",
                "filters": {"max_price": 300},
                "expected_features": ["results", "enhanced_query"]
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases):
            try:
                search_data = {
                    "query": test_case["query"],
                    "filters": test_case["filters"],
                    "limit": 10
                }
                
                async with self.session.post(f"{BACKEND_URL}/search/intelligent", json=search_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Check if all expected features are present
                        has_all_features = all(feature in result for feature in test_case["expected_features"])
                        has_results_structure = "results" in result and "total" in result
                        
                        if has_all_features and has_results_structure:
                            passed_tests += 1
                            results_count = len(result.get("results", []))
                            enhanced_query = result.get("enhanced_query", "")
                            self.log_test(f"Intelligent Search Case {i+1}", True, 
                                        f"Query: '{test_case['query']}' -> {results_count} results, Enhanced: '{enhanced_query}'")
                        else:
                            missing_features = [f for f in test_case["expected_features"] if f not in result]
                            self.log_test(f"Intelligent Search Case {i+1}", False, 
                                        f"Missing features: {missing_features}")
                    else:
                        self.log_test(f"Intelligent Search Case {i+1}", False, f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(f"Intelligent Search Case {i+1}", False, f"Error: {str(e)}")
                
        overall_success = passed_tests >= (total_tests * 0.75)  # 75% success rate
        self.log_test("Intelligent Search Overall", overall_success, f"{passed_tests}/{total_tests} test cases successful")
        return overall_success
        
    async def test_personalized_recommendations(self):
        """Test AI-powered personalized recommendations"""
        if not self.test_user_id:
            self.log_test("Personalized Recommendations", False, "No test user available")
            return False
            
        try:
            # First, add some user interactions (favorites, cart items)
            if self.test_listings:
                # Add to favorites
                for listing_id in self.test_listings[:2]:
                    try:
                        async with self.session.post(f"{BACKEND_URL}/user/{self.test_user_id}/favorites/{listing_id}") as response:
                            pass  # Don't fail if already exists
                    except:
                        pass
                        
                # Add to cart
                for listing_id in self.test_listings[:1]:
                    try:
                        cart_data = {"item_id": listing_id, "quantity": 1, "price": 299.99}
                        async with self.session.post(f"{BACKEND_URL}/user/{self.test_user_id}/cart", json=cart_data) as response:
                            pass  # Don't fail if already exists
                    except:
                        pass
            
            # Test recommendations endpoint
            async with self.session.get(f"{BACKEND_URL}/recommendations/{self.test_user_id}?limit=5") as response:
                if response.status == 200:
                    result = await response.json()
                    
                    required_fields = ["recommendations", "total", "user_profile"]
                    has_required_fields = all(field in result for field in required_fields)
                    
                    recommendations = result.get("recommendations", [])
                    user_profile = result.get("user_profile", {})
                    
                    if has_required_fields and isinstance(recommendations, list):
                        self.log_test("Personalized Recommendations", True, 
                                    f"Got {len(recommendations)} recommendations, Profile: {user_profile.get('interaction_count', 0)} interactions")
                        return True
                    else:
                        self.log_test("Personalized Recommendations", False, 
                                    f"Invalid response structure: {list(result.keys())}")
                        return False
                else:
                    self.log_test("Personalized Recommendations", False, f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Personalized Recommendations", False, f"Error: {str(e)}")
            return False
            
    async def test_search_history_management(self):
        """Test search history save and retrieve functionality"""
        if not self.test_user_id:
            self.log_test("Search History Management", False, "No test user available")
            return False
            
        try:
            # Test saving search history
            search_queries = ["gaming laptop", "wireless headphones", "vintage guitar"]
            saved_count = 0
            
            for query in search_queries:
                search_data = {
                    "user_id": self.test_user_id,
                    "query": query,
                    "results_count": 5
                }
                
                async with self.session.post(f"{BACKEND_URL}/search/save-history", json=search_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "saved" in result.get("message", "").lower() or "success" in result.get("message", "").lower():
                            saved_count += 1
            
            # Test retrieving search history
            async with self.session.get(f"{BACKEND_URL}/search/history/{self.test_user_id}?limit=10") as response:
                if response.status == 200:
                    result = await response.json()
                    history = result.get("history", [])
                    
                    if isinstance(history, list) and len(history) >= saved_count:
                        self.log_test("Search History Management", True, 
                                    f"Saved {saved_count} queries, Retrieved {len(history)} history records")
                        return True
                    else:
                        self.log_test("Search History Management", False, 
                                    f"Expected >= {saved_count} history records, got {len(history)}")
                        return False
                else:
                    self.log_test("Search History Management", False, f"Retrieve failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Search History Management", False, f"Error: {str(e)}")
            return False
            
    async def test_core_marketplace_functionality(self):
        """Test that existing marketplace functionality still works after AI features"""
        try:
            # Test health check
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                health_ok = response.status == 200
                
            # Test browse listings
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse") as response:
                browse_ok = response.status == 200
                if browse_ok:
                    result = await response.json()
                    browse_ok = isinstance(result, list)
                    
            # Test user profile
            profile_ok = False
            if self.test_user_id:
                async with self.session.get(f"{BACKEND_URL}/auth/profile/{self.test_user_id}") as response:
                    profile_ok = response.status == 200
                    
            # Test admin dashboard
            async with self.session.get(f"{BACKEND_URL}/admin/dashboard") as response:
                admin_ok = response.status == 200
                
            core_tests_passed = sum([health_ok, browse_ok, profile_ok, admin_ok])
            success = core_tests_passed >= 3  # At least 3 out of 4 should work
            
            self.log_test("Core Marketplace Functionality", success, 
                        f"{core_tests_passed}/4 core endpoints working (Health: {health_ok}, Browse: {browse_ok}, Profile: {profile_ok}, Admin: {admin_ok})")
            return success
            
        except Exception as e:
            self.log_test("Core Marketplace Functionality", False, f"Error: {str(e)}")
            return False
            
    async def test_ai_service_error_handling(self):
        """Test error handling when AI service might be unavailable"""
        try:
            # Test with invalid/empty queries to trigger fallback mechanisms
            test_cases = [
                {"query": "", "expected_fallback": True},
                {"query": "x", "expected_fallback": True},  # Too short
                {"query": "nonexistent_product_xyz_123", "expected_fallback": False}  # Valid but no results
            ]
            
            passed_tests = 0
            total_tests = len(test_cases)
            
            for i, test_case in enumerate(test_cases):
                # Test AI suggestions with edge cases
                search_data = {"query": test_case["query"]}
                
                async with self.session.post(f"{BACKEND_URL}/search/ai-suggestions", json=search_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        suggestions = result.get("suggestions", [])
                        
                        # Should always return a list, even if empty
                        if isinstance(suggestions, list):
                            passed_tests += 1
                            self.log_test(f"AI Error Handling Case {i+1}", True, 
                                        f"Query: '{test_case['query']}' -> {len(suggestions)} suggestions (graceful handling)")
                        else:
                            self.log_test(f"AI Error Handling Case {i+1}", False, 
                                        f"Invalid response type: {type(suggestions)}")
                    else:
                        self.log_test(f"AI Error Handling Case {i+1}", False, f"HTTP {response.status}")
                        
            success = passed_tests >= (total_tests * 0.8)
            self.log_test("AI Service Error Handling", success, f"{passed_tests}/{total_tests} edge cases handled gracefully")
            return success
            
        except Exception as e:
            self.log_test("AI Service Error Handling", False, f"Error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all AI search and recommendation tests"""
        print("🤖 Starting AI-Powered Search Endpoints Testing for Cataloro Marketplace")
        print("=" * 80)
        
        await self.setup_session()
        
        try:
            # Setup phase
            print("\n📋 SETUP PHASE")
            await self.create_test_user()
            await self.create_test_listings()
            
            # Core AI functionality tests
            print("\n🔍 AI SEARCH FUNCTIONALITY TESTS")
            await self.test_ai_search_suggestions()
            await self.test_intelligent_search()
            await self.test_personalized_recommendations()
            await self.test_search_history_management()
            
            # Integration and reliability tests
            print("\n🔧 INTEGRATION & RELIABILITY TESTS")
            await self.test_core_marketplace_functionality()
            await self.test_ai_service_error_handling()
            
            # Summary
            print("\n" + "=" * 80)
            print("📊 TEST SUMMARY")
            print("=" * 80)
            
            passed_tests = sum(1 for result in self.test_results if "✅ PASSED" in result["status"])
            total_tests = len(self.test_results)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests}")
            print(f"Failed: {total_tests - passed_tests}")
            print(f"Success Rate: {success_rate:.1f}%")
            
            # Detailed results
            print("\n📋 DETAILED RESULTS:")
            for result in self.test_results:
                print(f"{result['status']} {result['test']}: {result['details']}")
                
            # Overall assessment
            if success_rate >= 80:
                print(f"\n🎉 AI-POWERED SEARCH TESTING: ✅ SUCCESSFUL")
                print("All major AI search endpoints are working correctly!")
            elif success_rate >= 60:
                print(f"\n⚠️ AI-POWERED SEARCH TESTING: 🟡 PARTIAL SUCCESS")
                print("Most AI features working, some issues need attention.")
            else:
                print(f"\n❌ AI-POWERED SEARCH TESTING: ❌ NEEDS ATTENTION")
                print("Significant issues found with AI search functionality.")
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = AISearchTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())