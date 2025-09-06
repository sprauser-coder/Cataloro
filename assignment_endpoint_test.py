#!/usr/bin/env python3
"""
Assignment Endpoint Detailed Testing
Testing the PUT /api/user/bought-items/{item_id}/assign endpoint with detailed error logging
as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class AssignmentEndpointTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.demo_user_id = None
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def log_test_result(self, test_name, success, details="", error=""):
        """Log test results for summary"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{status}: {test_name}")
        if details:
            self.log(f"   Details: {details}")
        if error:
            self.log(f"   Error: {error}")
    
    def get_demo_user(self):
        """Get demo user for testing"""
        try:
            # Try to login as demo user
            login_data = {
                "email": "demo@cataloro.com",
                "username": "demo_user"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                self.demo_user_id = user.get('id')
                self.log(f"✅ Demo user logged in: {self.demo_user_id}")
                return True
            else:
                self.log(f"❌ Demo user login failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Demo user login error: {e}")
            return False
    
    def get_bought_items(self):
        """Get bought items for the demo user"""
        try:
            response = self.session.get(f"{BASE_URL}/user/bought-items/{self.demo_user_id}")
            if response.status_code == 200:
                items = response.json()
                self.log(f"✅ Found {len(items)} bought items")
                
                # Log details of each item
                for item in items:
                    item_id = item.get('id', 'Unknown')
                    title = item.get('title', 'Unknown')
                    price = item.get('price', 0)
                    self.log(f"   - {item_id}: {title} (€{price})")
                
                return items
            else:
                self.log(f"❌ Failed to get bought items: {response.status_code}")
                return []
        except Exception as e:
            self.log(f"❌ Error getting bought items: {e}")
            return []
    
    def get_user_baskets(self):
        """Get baskets for the demo user"""
        try:
            response = self.session.get(f"{BASE_URL}/user/baskets/{self.demo_user_id}")
            if response.status_code == 200:
                baskets = response.json()
                self.log(f"✅ Found {len(baskets)} baskets")
                
                # Log details of each basket
                for basket in baskets:
                    basket_id = basket.get('id', 'Unknown')
                    name = basket.get('name', 'Unknown')
                    self.log(f"   - {basket_id}: {name}")
                
                return baskets
            else:
                self.log(f"❌ Failed to get baskets: {response.status_code}")
                return []
        except Exception as e:
            self.log(f"❌ Error getting baskets: {e}")
            return []
    
    def create_test_basket(self):
        """Create a test basket for assignment testing"""
        try:
            basket_data = {
                "name": f"Test Assignment Basket {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test basket for assignment endpoint testing",
                "user_id": self.demo_user_id
            }
            
            response = self.session.post(f"{BASE_URL}/user/baskets", json=basket_data)
            if response.status_code == 200:
                data = response.json()
                basket_id = data.get('basket_id')
                self.log(f"✅ Created test basket: {basket_id}")
                return basket_id
            else:
                self.log(f"❌ Failed to create test basket: {response.status_code}")
                if response.content:
                    try:
                        error_data = response.json()
                        self.log(f"   Error details: {error_data}")
                    except:
                        self.log(f"   Response text: {response.text}")
                return None
        except Exception as e:
            self.log(f"❌ Error creating test basket: {e}")
            return None
    
    def test_assignment_endpoint_detailed(self, item_id, basket_id):
        """Test the assignment endpoint with detailed logging"""
        try:
            self.log(f"🔍 Testing assignment endpoint with:")
            self.log(f"   Item ID: {item_id}")
            self.log(f"   Basket ID: {basket_id}")
            
            assignment_data = {
                "basket_id": basket_id
            }
            
            self.log(f"🔍 Sending PUT request to: {BASE_URL}/user/bought-items/{item_id}/assign")
            self.log(f"🔍 Request payload: {json.dumps(assignment_data, indent=2)}")
            
            response = self.session.put(
                f"{BASE_URL}/user/bought-items/{item_id}/assign", 
                json=assignment_data
            )
            
            self.log(f"🔍 Response status code: {response.status_code}")
            self.log(f"🔍 Response headers: {dict(response.headers)}")
            
            if response.content:
                try:
                    response_data = response.json()
                    self.log(f"🔍 Response JSON: {json.dumps(response_data, indent=2)}")
                except:
                    self.log(f"🔍 Response text: {response.text}")
            else:
                self.log("🔍 Empty response body")
            
            if response.status_code == 200:
                self.log_test_result(
                    "Assignment Endpoint - Real Data",
                    True,
                    f"Successfully assigned item {item_id} to basket {basket_id}"
                )
                return True
            else:
                error_msg = "Unknown error"
                if response.content:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('detail', str(error_data))
                    except:
                        error_msg = response.text
                
                self.log_test_result(
                    "Assignment Endpoint - Real Data",
                    False,
                    f"Failed to assign item {item_id} to basket {basket_id}",
                    error_msg
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Assignment Endpoint - Real Data",
                False,
                error=str(e)
            )
            return False
    
    def test_assignment_validation(self):
        """Test assignment endpoint validation"""
        try:
            # Test 1: Missing basket_id
            self.log("🔍 Testing validation: Missing basket_id")
            test_item_id = "test_item_123"
            
            response = self.session.put(
                f"{BASE_URL}/user/bought-items/{test_item_id}/assign", 
                json={}
            )
            
            self.log(f"🔍 Response status: {response.status_code}")
            if response.content:
                try:
                    error_data = response.json()
                    self.log(f"🔍 Error response: {json.dumps(error_data, indent=2)}")
                except:
                    self.log(f"🔍 Response text: {response.text}")
            
            if response.status_code == 400:
                self.log_test_result(
                    "Assignment Validation - Missing basket_id",
                    True,
                    "Correctly rejected missing basket_id"
                )
            else:
                self.log_test_result(
                    "Assignment Validation - Missing basket_id",
                    False,
                    f"Expected 400 but got {response.status_code}"
                )
            
            # Test 2: Non-existent basket
            self.log("🔍 Testing validation: Non-existent basket")
            
            response = self.session.put(
                f"{BASE_URL}/user/bought-items/{test_item_id}/assign", 
                json={"basket_id": "non_existent_basket_123"}
            )
            
            self.log(f"🔍 Response status: {response.status_code}")
            if response.content:
                try:
                    error_data = response.json()
                    self.log(f"🔍 Error response: {json.dumps(error_data, indent=2)}")
                except:
                    self.log(f"🔍 Response text: {response.text}")
            
            if response.status_code == 404:
                self.log_test_result(
                    "Assignment Validation - Non-existent basket",
                    True,
                    "Correctly rejected non-existent basket"
                )
            else:
                self.log_test_result(
                    "Assignment Validation - Non-existent basket",
                    False,
                    f"Expected 404 but got {response.status_code}"
                )
            
        except Exception as e:
            self.log_test_result(
                "Assignment Validation Tests",
                False,
                error=str(e)
            )
    
    def test_specific_item_from_review(self, basket_id):
        """Test with the specific item ID mentioned in the review request"""
        specific_item_id = "tender_0ec81084-3c4b-48d5-8cf3-fa6c075bd489"
        
        self.log(f"🔍 Testing with specific item from review: {specific_item_id}")
        
        return self.test_assignment_endpoint_detailed(specific_item_id, basket_id)
    
    def run_comprehensive_test(self):
        """Run comprehensive assignment endpoint testing"""
        self.log("🚀 Starting Assignment Endpoint Detailed Testing")
        self.log("=" * 60)
        
        # 1. Get demo user
        if not self.get_demo_user():
            self.log("❌ Cannot proceed without demo user")
            return
        
        # 2. Get bought items
        self.log("\n🛒 Getting bought items...")
        bought_items = self.get_bought_items()
        
        # 3. Get existing baskets
        self.log("\n🧺 Getting existing baskets...")
        baskets = self.get_user_baskets()
        
        # 4. Create test basket
        self.log("\n🆕 Creating test basket...")
        test_basket_id = self.create_test_basket()
        
        if not test_basket_id:
            self.log("❌ Cannot proceed without test basket")
            return
        
        # 5. Test validation
        self.log("\n✅ Testing assignment validation...")
        self.test_assignment_validation()
        
        # 6. Test with real data if available
        if bought_items:
            self.log("\n🎯 Testing with real bought items...")
            for item in bought_items[:2]:  # Test first 2 items
                item_id = item.get('id')
                if item_id:
                    self.test_assignment_endpoint_detailed(item_id, test_basket_id)
        else:
            self.log("\n⚠️ No bought items found for real data testing")
        
        # 7. Test with specific item from review
        self.log("\n🔍 Testing with specific item from review request...")
        self.test_specific_item_from_review(test_basket_id)
        
        # 8. Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "=" * 60)
        self.log("📊 TEST SUMMARY")
        self.log("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {passed_tests}")
        self.log(f"Failed: {failed_tests}")
        self.log(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests > 0:
            self.log("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    self.log(f"  - {result['test']}: {result['error']}")
        
        self.log("\n🎯 ASSIGNMENT ENDPOINT TESTING COMPLETE")

if __name__ == "__main__":
    tester = AssignmentEndpointTester()
    tester.run_comprehensive_test()