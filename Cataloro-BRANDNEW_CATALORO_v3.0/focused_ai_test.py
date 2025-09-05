#!/usr/bin/env python3
"""
Focused AI Search Testing - Specific Review Requirements
Testing the exact scenarios mentioned in the review request
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BACKEND_URL = "https://market-evolution-1.preview.emergentagent.com/api"

class FocusedAITester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_user_id = "1e731c02-27b3-4f33-b1e1-18ba7d555020"  # Use existing admin user
        
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
        
    async def test_ai_search_suggestions_realistic_queries(self):
        """Test AI Search Suggestions with realistic queries from review"""
        realistic_queries = [
            "gaming laptop",
            "wireless headphones", 
            "vintage guitar"
        ]
        
        passed_tests = 0
        total_tests = len(realistic_queries)
        
        for query in realistic_queries:
            try:
                search_data = {
                    "query": query,
                    "context": {
                        "previous_searches": ["electronics", "music"]
                    }
                }
                
                async with self.session.post(f"{BACKEND_URL}/search/ai-suggestions", json=search_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        suggestions = result.get("suggestions", [])
                        
                        if isinstance(suggestions, list):
                            passed_tests += 1
                            self.log_test(f"AI Suggestions: '{query}'", True, 
                                        f"Got {len(suggestions)} suggestions: {suggestions}")
                        else:
                            self.log_test(f"AI Suggestions: '{query}'", False, 
                                        f"Invalid response format")
                    else:
                        self.log_test(f"AI Suggestions: '{query}'", False, 
                                    f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(f"AI Suggestions: '{query}'", False, f"Error: {str(e)}")
                
        return passed_tests == total_tests
        
    async def test_intelligent_search_with_filters(self):
        """Test Intelligent Search with different search queries and filters"""
        test_cases = [
            {
                "name": "Gaming Laptop with Price Filter",
                "query": "gaming laptop",
                "filters": {"max_price": 2000, "category": "Electronics"}
            },
            {
                "name": "Wireless Headphones with Category Filter",
                "query": "wireless headphones",
                "filters": {"category": "Electronics", "condition": "new"}
            },
            {
                "name": "Vintage Guitar with Condition Filter",
                "query": "vintage guitar",
                "filters": {"condition": "used", "min_price": 300}
            }
        ]
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for test_case in test_cases:
            try:
                search_data = {
                    "query": test_case["query"],
                    "filters": test_case["filters"],
                    "limit": 10
                }
                
                async with self.session.post(f"{BACKEND_URL}/search/intelligent", json=search_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Check required fields
                        required_fields = ["results", "total", "enhanced_query", "search_intent", "applied_filters"]
                        has_required = all(field in result for field in required_fields)
                        
                        if has_required:
                            passed_tests += 1
                            results_count = len(result.get("results", []))
                            enhanced_query = result.get("enhanced_query", "")
                            applied_filters = result.get("applied_filters", {})
                            
                            self.log_test(f"Intelligent Search: {test_case['name']}", True, 
                                        f"Query: '{test_case['query']}' -> {results_count} results, Enhanced: '{enhanced_query}', Filters: {applied_filters}")
                        else:
                            missing = [f for f in required_fields if f not in result]
                            self.log_test(f"Intelligent Search: {test_case['name']}", False, 
                                        f"Missing fields: {missing}")
                    else:
                        self.log_test(f"Intelligent Search: {test_case['name']}", False, 
                                    f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(f"Intelligent Search: {test_case['name']}", False, f"Error: {str(e)}")
                
        return passed_tests >= (total_tests * 0.8)  # 80% success rate
        
    async def test_personalized_recommendations_user_id(self):
        """Test personalized recommendations for specific user ID"""
        try:
            async with self.session.get(f"{BACKEND_URL}/recommendations/{self.test_user_id}?limit=8") as response:
                if response.status == 200:
                    result = await response.json()
                    
                    required_fields = ["recommendations", "total", "user_profile"]
                    has_required = all(field in result for field in required_fields)
                    
                    recommendations = result.get("recommendations", [])
                    user_profile = result.get("user_profile", {})
                    
                    if has_required and isinstance(recommendations, list):
                        self.log_test("Personalized Recommendations", True, 
                                    f"User {self.test_user_id}: {len(recommendations)} recommendations, Profile: {user_profile}")
                        return True
                    else:
                        self.log_test("Personalized Recommendations", False, 
                                    f"Invalid response structure")
                        return False
                else:
                    self.log_test("Personalized Recommendations", False, 
                                f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Personalized Recommendations", False, f"Error: {str(e)}")
            return False
            
    async def test_search_history_save_and_retrieve(self):
        """Test search history save and retrieve functionality"""
        try:
            # Save search history for realistic queries
            realistic_searches = [
                {"query": "gaming laptop", "results_count": 3},
                {"query": "wireless headphones", "results_count": 5},
                {"query": "vintage guitar", "results_count": 2}
            ]
            
            saved_count = 0
            for search in realistic_searches:
                search_data = {
                    "user_id": self.test_user_id,
                    "query": search["query"],
                    "results_count": search["results_count"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/search/save-history", json=search_data) as response:
                    if response.status == 200:
                        saved_count += 1
            
            # Retrieve search history
            async with self.session.get(f"{BACKEND_URL}/search/history/{self.test_user_id}?limit=10") as response:
                if response.status == 200:
                    result = await response.json()
                    history = result.get("history", [])
                    
                    if isinstance(history, list) and len(history) >= saved_count:
                        self.log_test("Search History Management", True, 
                                    f"Saved {saved_count} searches, Retrieved {len(history)} history records")
                        return True
                    else:
                        self.log_test("Search History Management", False, 
                                    f"Expected >= {saved_count} records, got {len(history)}")
                        return False
                else:
                    self.log_test("Search History Management", False, 
                                f"Retrieve failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Search History Management", False, f"Error: {str(e)}")
            return False
            
    async def test_core_functionality_integrity(self):
        """Verify existing marketplace functionality still works after AI features"""
        core_endpoints = [
            {"name": "Health Check", "url": f"{BACKEND_URL}/health", "method": "GET"},
            {"name": "Browse Listings", "url": f"{BACKEND_URL}/marketplace/browse", "method": "GET"},
            {"name": "Admin Dashboard", "url": f"{BACKEND_URL}/admin/dashboard", "method": "GET"},
            {"name": "User Profile", "url": f"{BACKEND_URL}/auth/profile/{self.test_user_id}", "method": "GET"}
        ]
        
        passed_tests = 0
        total_tests = len(core_endpoints)
        
        for endpoint in core_endpoints:
            try:
                async with self.session.get(endpoint["url"]) as response:
                    if response.status == 200:
                        passed_tests += 1
                        self.log_test(f"Core Functionality: {endpoint['name']}", True, 
                                    f"Status: {response.status}")
                    else:
                        self.log_test(f"Core Functionality: {endpoint['name']}", False, 
                                    f"Status: {response.status}")
                        
            except Exception as e:
                self.log_test(f"Core Functionality: {endpoint['name']}", False, f"Error: {str(e)}")
                
        success = passed_tests >= (total_tests * 0.8)  # 80% success rate
        self.log_test("Core Functionality Overall", success, 
                    f"{passed_tests}/{total_tests} core endpoints working")
        return success
        
    async def test_ai_service_fallback_mechanisms(self):
        """Test error scenarios when AI service might be unavailable"""
        fallback_test_cases = [
            {"query": "", "description": "Empty query"},
            {"query": "a", "description": "Single character query"},
            {"query": "xyz123nonexistent", "description": "Non-existent product query"},
            {"query": "special!@#$%characters", "description": "Special characters query"}
        ]
        
        passed_tests = 0
        total_tests = len(fallback_test_cases)
        
        for test_case in fallback_test_cases:
            try:
                # Test AI suggestions fallback
                search_data = {"query": test_case["query"]}
                
                async with self.session.post(f"{BACKEND_URL}/search/ai-suggestions", json=search_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        suggestions = result.get("suggestions", [])
                        
                        # Should always return a list (graceful fallback)
                        if isinstance(suggestions, list):
                            passed_tests += 1
                            self.log_test(f"Fallback Test: {test_case['description']}", True, 
                                        f"Query: '{test_case['query']}' -> {len(suggestions)} suggestions (graceful)")
                        else:
                            self.log_test(f"Fallback Test: {test_case['description']}", False, 
                                        f"Invalid response type")
                    else:
                        self.log_test(f"Fallback Test: {test_case['description']}", False, 
                                    f"HTTP {response.status}")
                        
            except Exception as e:
                self.log_test(f"Fallback Test: {test_case['description']}", False, f"Error: {str(e)}")
                
        success = passed_tests >= (total_tests * 0.75)  # 75% success rate
        self.log_test("AI Fallback Mechanisms", success, 
                    f"{passed_tests}/{total_tests} fallback scenarios handled")
        return success
        
    async def run_focused_tests(self):
        """Run focused tests for the specific review requirements"""
        print("🎯 FOCUSED AI SEARCH TESTING - Review Requirements")
        print("=" * 70)
        
        await self.setup_session()
        
        try:
            # Test specific requirements from review
            print("\n1️⃣ AI SEARCH SUGGESTIONS with realistic queries")
            ai_suggestions_ok = await self.test_ai_search_suggestions_realistic_queries()
            
            print("\n2️⃣ INTELLIGENT SEARCH with different queries and filters")
            intelligent_search_ok = await self.test_intelligent_search_with_filters()
            
            print("\n3️⃣ PERSONALIZED RECOMMENDATIONS for user ID")
            recommendations_ok = await self.test_personalized_recommendations_user_id()
            
            print("\n4️⃣ SEARCH HISTORY save and retrieve")
            search_history_ok = await self.test_search_history_save_and_retrieve()
            
            print("\n5️⃣ CORE FUNCTIONALITY integrity check")
            core_functionality_ok = await self.test_core_functionality_integrity()
            
            print("\n6️⃣ ERROR HANDLING and fallback mechanisms")
            fallback_ok = await self.test_ai_service_fallback_mechanisms()
            
            # Summary
            print("\n" + "=" * 70)
            print("📊 FOCUSED TEST SUMMARY")
            print("=" * 70)
            
            passed_tests = sum(1 for result in self.test_results if "✅ PASSED" in result["status"])
            total_tests = len(self.test_results)
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            
            # Major requirements check
            major_requirements = [
                ("AI Search Suggestions", ai_suggestions_ok),
                ("Intelligent Search", intelligent_search_ok),
                ("Personalized Recommendations", recommendations_ok),
                ("Search History Management", search_history_ok),
                ("Core Functionality", core_functionality_ok),
                ("Error Handling", fallback_ok)
            ]
            
            major_passed = sum(1 for _, passed in major_requirements if passed)
            major_total = len(major_requirements)
            
            print(f"Total Individual Tests: {total_tests}")
            print(f"Individual Tests Passed: {passed_tests}")
            print(f"Individual Success Rate: {success_rate:.1f}%")
            print(f"\nMajor Requirements: {major_passed}/{major_total}")
            
            for req_name, passed in major_requirements:
                status = "✅ PASSED" if passed else "❌ FAILED"
                print(f"  {status} {req_name}")
                
            # Overall assessment
            if major_passed == major_total and success_rate >= 90:
                print(f"\n🎉 FOCUSED AI TESTING: ✅ EXCELLENT")
                print("All AI search requirements fully satisfied!")
            elif major_passed >= (major_total * 0.8) and success_rate >= 80:
                print(f"\n✅ FOCUSED AI TESTING: ✅ SUCCESSFUL")
                print("AI search functionality working as expected!")
            elif major_passed >= (major_total * 0.6):
                print(f"\n⚠️ FOCUSED AI TESTING: 🟡 PARTIAL SUCCESS")
                print("Most AI features working, minor issues detected.")
            else:
                print(f"\n❌ FOCUSED AI TESTING: ❌ NEEDS ATTENTION")
                print("Significant issues with AI search functionality.")
                
        finally:
            await self.cleanup_session()

async def main():
    """Main test execution function"""
    tester = FocusedAITester()
    await tester.run_focused_tests()

if __name__ == "__main__":
    asyncio.run(main())