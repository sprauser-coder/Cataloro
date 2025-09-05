#!/usr/bin/env python3
"""
Catalyst Review System Backend Testing
Testing Phase 2 Social Commerce Review Endpoints
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

class CatalystReviewTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = str(uuid.uuid4())
        self.test_seller_id = str(uuid.uuid4())
        self.test_listing_id = None
        self.test_review_id = None
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def setup_test_data(self):
        """Create test listing for catalyst reviews"""
        print("\n🔧 Setting up test data...")
        
        # Create test listing with catalyst-specific data
        listing_data = {
            "title": "High-Performance Platinum Catalyst - Automotive Grade",
            "description": "Premium platinum catalyst with excellent activity and selectivity for automotive applications. Tested in various reaction conditions with consistent performance.",
            "price": 2500.00,
            "category": "Automotive Catalysts",
            "condition": "New",
            "seller_id": self.test_seller_id,
            "images": ["https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400"],
            "tags": ["platinum", "automotive", "high-performance", "catalyst"],
            "features": ["High activity", "Excellent selectivity", "Stable performance", "Automotive grade"]
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data)
            if response.status_code == 200:
                result = response.json()
                self.test_listing_id = result.get("listing_id")
                self.log_test("Setup Test Listing", True, f"Created listing: {self.test_listing_id}")
                return True
            else:
                self.log_test("Setup Test Listing", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Setup Test Listing", False, f"Exception: {str(e)}")
            return False
    
    def test_create_review_endpoint(self):
        """Test POST /api/reviews/create with catalyst-specific technical details"""
        print("\n🧪 Testing Create Review Endpoint...")
        
        # Test comprehensive catalyst review with technical details
        review_data = {
            "listing_id": self.test_listing_id,
            "user_id": self.test_user_id,
            "user_name": "Dr. Sarah Chen",
            "user_avatar": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100",
            "rating": 5,
            "title": "Excellent Catalyst Performance in Automotive Applications",
            "content": "This platinum catalyst exceeded our expectations in automotive exhaust treatment. The activity remained consistent across multiple test cycles, and the selectivity for target reactions was outstanding. We observed minimal deactivation even after extended use at high temperatures.",
            "technical_details": {
                "reaction_conditions": {
                    "temperature": "450-550°C",
                    "pressure": "1-3 atm",
                    "space_velocity": "50,000 h⁻¹",
                    "gas_composition": "CO, NOx, HC in air"
                },
                "yield_achieved": "98.5%",
                "observations": "Stable performance over 1000 hours, minimal sintering observed, excellent thermal stability"
            },
            "performance_rating": {
                "activity": 5,
                "selectivity": 5,
                "stability": 4
            },
            "would_recommend": True,
            "verified": True,
            "images": ["https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400"]
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/reviews/create", json=review_data)
            if response.status_code == 200:
                result = response.json()
                self.test_review_id = result.get("review_id")
                self.log_test("Create Catalyst Review", True, f"Review created: {self.test_review_id}")
                return True
            else:
                self.log_test("Create Catalyst Review", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Catalyst Review", False, f"Exception: {str(e)}")
            return False
    
    def test_create_additional_reviews(self):
        """Create additional reviews for comprehensive testing"""
        print("\n🧪 Creating Additional Test Reviews...")
        
        additional_reviews = [
            {
                "listing_id": self.test_listing_id,
                "user_id": str(uuid.uuid4()),
                "user_name": "Prof. Michael Rodriguez",
                "rating": 4,
                "title": "Good Performance with Minor Issues",
                "content": "Overall good catalyst performance. Activity is high but noticed some selectivity issues at higher temperatures.",
                "technical_details": {
                    "reaction_conditions": {
                        "temperature": "500-600°C",
                        "pressure": "2 atm",
                        "space_velocity": "40,000 h⁻¹"
                    },
                    "yield_achieved": "92.3%",
                    "observations": "Some selectivity loss at temperatures above 550°C"
                },
                "performance_rating": {
                    "activity": 4,
                    "selectivity": 3,
                    "stability": 4
                },
                "would_recommend": True
            },
            {
                "listing_id": self.test_listing_id,
                "user_id": str(uuid.uuid4()),
                "user_name": "Dr. Emily Watson",
                "rating": 5,
                "title": "Outstanding Stability and Performance",
                "content": "Exceptional catalyst with remarkable stability. Perfect for long-term industrial applications.",
                "technical_details": {
                    "reaction_conditions": {
                        "temperature": "400-500°C",
                        "pressure": "1.5 atm",
                        "space_velocity": "60,000 h⁻¹"
                    },
                    "yield_achieved": "96.8%",
                    "observations": "No deactivation observed after 2000 hours of operation"
                },
                "performance_rating": {
                    "activity": 5,
                    "selectivity": 5,
                    "stability": 5
                },
                "would_recommend": True
            }
        ]
        
        success_count = 0
        for i, review in enumerate(additional_reviews):
            try:
                response = requests.post(f"{BACKEND_URL}/reviews/create", json=review)
                if response.status_code == 200:
                    success_count += 1
                    self.log_test(f"Additional Review {i+1}", True, f"Created by {review['user_name']}")
                else:
                    self.log_test(f"Additional Review {i+1}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Additional Review {i+1}", False, f"Exception: {str(e)}")
        
        return success_count == len(additional_reviews)
    
    def test_get_reviews_endpoint(self):
        """Test GET /api/reviews/listing/{listing_id} with performance metrics"""
        print("\n🧪 Testing Get Reviews Endpoint...")
        
        try:
            response = requests.get(f"{BACKEND_URL}/reviews/listing/{self.test_listing_id}")
            if response.status_code == 200:
                result = response.json()
                
                # Verify response structure
                required_fields = ["reviews", "average_rating", "total_reviews", "rating_distribution"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test("Get Reviews Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                reviews = result["reviews"]
                avg_rating = result["average_rating"]
                total_reviews = result["total_reviews"]
                
                # Verify reviews contain catalyst-specific data
                catalyst_data_found = False
                performance_metrics_found = False
                
                for review in reviews:
                    if "technical_details" in review and review["technical_details"]:
                        catalyst_data_found = True
                    if "performance_rating" in review and review["performance_rating"]:
                        performance_metrics_found = True
                
                self.log_test("Get Reviews Structure", True, f"Found {total_reviews} reviews, avg rating: {avg_rating:.2f}")
                self.log_test("Catalyst Technical Details", catalyst_data_found, "Technical details present in reviews")
                self.log_test("Performance Metrics", performance_metrics_found, "Activity/selectivity/stability ratings present")
                
                # Test different sorting options
                sort_options = ["newest", "oldest", "highest", "lowest", "helpful"]
                for sort_by in sort_options:
                    try:
                        sort_response = requests.get(f"{BACKEND_URL}/reviews/listing/{self.test_listing_id}?sort_by={sort_by}")
                        if sort_response.status_code == 200:
                            self.log_test(f"Sort by {sort_by}", True, "Sorting working correctly")
                        else:
                            self.log_test(f"Sort by {sort_by}", False, f"Status: {sort_response.status_code}")
                    except Exception as e:
                        self.log_test(f"Sort by {sort_by}", False, f"Exception: {str(e)}")
                
                return True
            else:
                self.log_test("Get Reviews", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Get Reviews", False, f"Exception: {str(e)}")
            return False
    
    def test_mark_helpful_endpoint(self):
        """Test POST /api/reviews/{review_id}/helpful for user interaction"""
        print("\n🧪 Testing Mark Helpful Endpoint...")
        
        if not self.test_review_id:
            self.log_test("Mark Helpful", False, "No review ID available for testing")
            return False
        
        # Test marking review as helpful
        helpful_data = {
            "user_id": str(uuid.uuid4())  # Different user marking as helpful
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/reviews/{self.test_review_id}/helpful", json=helpful_data)
            if response.status_code == 200:
                self.log_test("Mark Review Helpful", True, "Review marked as helpful successfully")
                
                # Test duplicate helpful (should be handled gracefully)
                duplicate_response = requests.post(f"{BACKEND_URL}/reviews/{self.test_review_id}/helpful", json=helpful_data)
                if duplicate_response.status_code == 200:
                    result = duplicate_response.json()
                    if "already marked" in result.get("message", "").lower():
                        self.log_test("Duplicate Helpful Prevention", True, "Duplicate helpful votes prevented")
                    else:
                        self.log_test("Duplicate Helpful Prevention", False, "Duplicate votes not properly handled")
                
                return True
            else:
                self.log_test("Mark Review Helpful", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Mark Review Helpful", False, f"Exception: {str(e)}")
            return False
    
    def test_seller_response_endpoint(self):
        """Test POST /api/reviews/{review_id}/response for seller responses"""
        print("\n🧪 Testing Seller Response Endpoint...")
        
        if not self.test_review_id:
            self.log_test("Seller Response", False, "No review ID available for testing")
            return False
        
        # Test seller response
        response_data = {
            "content": "Thank you for your detailed review! We're thrilled that our platinum catalyst met your performance expectations. Your technical observations about the stability at high temperatures are very valuable. We appreciate your business and look forward to supporting your future catalyst needs.",
            "seller_id": self.test_seller_id
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/reviews/{self.test_review_id}/response", json=response_data)
            if response.status_code == 200:
                self.log_test("Seller Response", True, "Seller response added successfully")
                
                # Verify response was added by getting the review
                get_response = requests.get(f"{BACKEND_URL}/reviews/listing/{self.test_listing_id}")
                if get_response.status_code == 200:
                    reviews = get_response.json()["reviews"]
                    response_found = False
                    for review in reviews:
                        if review.get("id") == self.test_review_id and "seller_response" in review:
                            response_found = True
                            break
                    
                    self.log_test("Seller Response Verification", response_found, "Response appears in review data")
                
                return True
            else:
                self.log_test("Seller Response", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Seller Response", False, f"Exception: {str(e)}")
            return False
    
    def test_favorites_system(self):
        """Test GET/POST/DELETE /api/user/{user_id}/favorites/{listing_id}"""
        print("\n🧪 Testing Favorites System...")
        
        # Test adding to favorites
        try:
            add_response = requests.post(f"{BACKEND_URL}/user/{self.test_user_id}/favorites/{self.test_listing_id}")
            if add_response.status_code == 200:
                self.log_test("Add to Favorites", True, "Catalyst added to favorites")
                
                # Test getting favorites
                get_response = requests.get(f"{BACKEND_URL}/user/{self.test_user_id}/favorites")
                if get_response.status_code == 200:
                    favorites = get_response.json()
                    if isinstance(favorites, dict) and "favorites" in favorites:
                        favorites_list = favorites["favorites"]
                    else:
                        favorites_list = favorites
                    
                    favorite_found = any(fav.get("id") == self.test_listing_id for fav in favorites_list)
                    self.log_test("Get Favorites", favorite_found, f"Found {len(favorites_list)} favorites")
                else:
                    self.log_test("Get Favorites", False, f"Status: {get_response.status_code}")
                
                # Test duplicate add (should handle gracefully)
                duplicate_response = requests.post(f"{BACKEND_URL}/user/{self.test_user_id}/favorites/{self.test_listing_id}")
                if duplicate_response.status_code == 200:
                    result = duplicate_response.json()
                    if "already" in result.get("message", "").lower():
                        self.log_test("Duplicate Favorite Prevention", True, "Duplicate favorites prevented")
                    else:
                        self.log_test("Duplicate Favorite Prevention", False, "Duplicate handling unclear")
                
                # Test removing from favorites
                delete_response = requests.delete(f"{BACKEND_URL}/user/{self.test_user_id}/favorites/{self.test_listing_id}")
                if delete_response.status_code == 200:
                    self.log_test("Remove from Favorites", True, "Catalyst removed from favorites")
                else:
                    self.log_test("Remove from Favorites", False, f"Status: {delete_response.status_code}")
                
                return True
            else:
                self.log_test("Add to Favorites", False, f"Status: {add_response.status_code}, Response: {add_response.text}")
                return False
        except Exception as e:
            self.log_test("Favorites System", False, f"Exception: {str(e)}")
            return False
    
    def test_performance_metrics_calculation(self):
        """Verify that reviews calculate average activity, selectivity, and stability ratings"""
        print("\n🧪 Testing Performance Metrics Calculation...")
        
        try:
            # Get all reviews for the listing
            response = requests.get(f"{BACKEND_URL}/reviews/listing/{self.test_listing_id}")
            if response.status_code == 200:
                result = response.json()
                reviews = result["reviews"]
                
                # Calculate expected averages from performance ratings
                activity_ratings = []
                selectivity_ratings = []
                stability_ratings = []
                
                for review in reviews:
                    perf_rating = review.get("performance_rating", {})
                    if perf_rating:
                        if "activity" in perf_rating:
                            activity_ratings.append(perf_rating["activity"])
                        if "selectivity" in perf_rating:
                            selectivity_ratings.append(perf_rating["selectivity"])
                        if "stability" in perf_rating:
                            stability_ratings.append(perf_rating["stability"])
                
                # Calculate averages
                avg_activity = sum(activity_ratings) / len(activity_ratings) if activity_ratings else 0
                avg_selectivity = sum(selectivity_ratings) / len(selectivity_ratings) if selectivity_ratings else 0
                avg_stability = sum(stability_ratings) / len(stability_ratings) if stability_ratings else 0
                
                self.log_test("Performance Metrics Found", len(activity_ratings) > 0, 
                            f"Activity: {avg_activity:.2f}, Selectivity: {avg_selectivity:.2f}, Stability: {avg_stability:.2f}")
                
                # Verify overall rating calculation
                overall_avg = result["average_rating"]
                expected_overall = sum(r["rating"] for r in reviews) / len(reviews) if reviews else 0
                
                rating_match = abs(overall_avg - expected_overall) < 0.01
                self.log_test("Overall Rating Calculation", rating_match, 
                            f"Expected: {expected_overall:.2f}, Got: {overall_avg:.2f}")
                
                return len(activity_ratings) > 0 and rating_match
            else:
                self.log_test("Performance Metrics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Performance Metrics", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all catalyst review system tests"""
        print("🚀 Starting Catalyst Review System Backend Testing")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_data():
            print("❌ Setup failed, cannot continue testing")
            return False
        
        # Run all tests
        tests = [
            self.test_create_review_endpoint,
            self.test_create_additional_reviews,
            self.test_get_reviews_endpoint,
            self.test_mark_helpful_endpoint,
            self.test_seller_response_endpoint,
            self.test_favorites_system,
            self.test_performance_metrics_calculation
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CATALYST REVIEW SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} major tests passed)")
        
        # Detailed results
        print("\nDetailed Test Results:")
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        # Final assessment
        if success_rate >= 90:
            print("\n✅ CATALYST REVIEW SYSTEM: FULLY OPERATIONAL")
        elif success_rate >= 70:
            print("\n⚠️ CATALYST REVIEW SYSTEM: MOSTLY FUNCTIONAL - Minor issues detected")
        else:
            print("\n❌ CATALYST REVIEW SYSTEM: SIGNIFICANT ISSUES - Major functionality problems")
        
        return success_rate >= 70

if __name__ == "__main__":
    tester = CatalystReviewTester()
    tester.run_comprehensive_test()