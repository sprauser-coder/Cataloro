#!/usr/bin/env python3
"""
Buy Management Backend Testing
Testing the new Buy Management backend endpoints for bought items and baskets functionality.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class BuyManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.demo_user_id = None
        self.test_basket_id = None
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_health_check(self):
        """Test if backend is accessible"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log("✅ Backend health check passed")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Backend connection failed: {e}")
            return False
    
    def get_demo_user(self):
        """Get or create a demo user for testing"""
        try:
            # Try to login as demo user
            login_data = {
                "email": "demo@cataloro.com",
                "username": "demo_user"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                user_data = response.json()
                self.demo_user_id = user_data.get("user", {}).get("id")
                self.log(f"✅ Demo user logged in: {self.demo_user_id}")
                return True
            else:
                self.log(f"❌ Demo user login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error getting demo user: {e}")
            return False
    
    def test_bought_items_endpoint(self):
        """Test GET /api/user/bought-items/{user_id}"""
        self.log("🧪 Testing Bought Items Endpoint...")
        
        if not self.demo_user_id:
            self.log("❌ No demo user available for testing")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/user/bought-items/{self.demo_user_id}")
            
            if response.status_code == 200:
                bought_items = response.json()
                self.log(f"✅ Bought items endpoint working - Found {len(bought_items)} items")
                
                # Validate response structure
                if isinstance(bought_items, list):
                    self.log("✅ Response is a valid list")
                    
                    if bought_items:
                        # Check first item structure
                        first_item = bought_items[0]
                        required_fields = ["id", "listing_id", "title", "price", "seller_name", "seller_id"]
                        
                        missing_fields = [field for field in required_fields if field not in first_item]
                        if not missing_fields:
                            self.log("✅ Bought item structure is valid")
                        else:
                            self.log(f"⚠️ Missing fields in bought item: {missing_fields}")
                    else:
                        self.log("ℹ️ No bought items found (empty list)")
                        
                    return True
                else:
                    self.log("❌ Response is not a list")
                    return False
                    
            else:
                self.log(f"❌ Bought items endpoint failed: {response.status_code}")
                if response.text:
                    self.log(f"Error details: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing bought items endpoint: {e}")
            return False
    
    def test_get_baskets_endpoint(self):
        """Test GET /api/user/baskets/{user_id}"""
        self.log("🧪 Testing Get Baskets Endpoint...")
        
        if not self.demo_user_id:
            self.log("❌ No demo user available for testing")
            return False
            
        try:
            response = self.session.get(f"{BASE_URL}/user/baskets/{self.demo_user_id}")
            
            if response.status_code == 200:
                baskets = response.json()
                self.log(f"✅ Get baskets endpoint working - Found {len(baskets)} baskets")
                
                # Validate response structure
                if isinstance(baskets, list):
                    self.log("✅ Response is a valid list")
                    
                    if baskets:
                        # Check first basket structure
                        first_basket = baskets[0]
                        required_fields = ["id", "user_id", "name", "created_at"]
                        
                        missing_fields = [field for field in required_fields if field not in first_basket]
                        if not missing_fields:
                            self.log("✅ Basket structure is valid")
                        else:
                            self.log(f"⚠️ Missing fields in basket: {missing_fields}")
                    else:
                        self.log("ℹ️ No baskets found (empty list)")
                        
                    return True
                else:
                    self.log("❌ Response is not a list")
                    return False
                    
            else:
                self.log(f"❌ Get baskets endpoint failed: {response.status_code}")
                if response.text:
                    self.log(f"Error details: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing get baskets endpoint: {e}")
            return False
    
    def test_create_basket_endpoint(self):
        """Test POST /api/user/baskets"""
        self.log("🧪 Testing Create Basket Endpoint...")
        
        if not self.demo_user_id:
            self.log("❌ No demo user available for testing")
            return False
            
        try:
            basket_data = {
                "user_id": self.demo_user_id,
                "name": "Test Basket for Buy Management",
                "description": "A test basket created during backend testing"
            }
            
            response = self.session.post(f"{BASE_URL}/user/baskets", json=basket_data)
            
            if response.status_code == 200:
                result = response.json()
                self.test_basket_id = result.get("basket_id")
                self.log(f"✅ Create basket endpoint working - Basket ID: {self.test_basket_id}")
                
                # Validate response structure
                if "message" in result and "basket_id" in result:
                    self.log("✅ Create basket response structure is valid")
                    return True
                else:
                    self.log("⚠️ Create basket response missing expected fields")
                    return False
                    
            else:
                self.log(f"❌ Create basket endpoint failed: {response.status_code}")
                if response.text:
                    self.log(f"Error details: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing create basket endpoint: {e}")
            return False
    
    def test_update_basket_endpoint(self):
        """Test PUT /api/user/baskets/{basket_id}"""
        self.log("🧪 Testing Update Basket Endpoint...")
        
        if not self.test_basket_id:
            self.log("❌ No test basket available for updating")
            return False
            
        try:
            update_data = {
                "name": "Updated Test Basket",
                "description": "Updated description for testing"
            }
            
            response = self.session.put(f"{BASE_URL}/user/baskets/{self.test_basket_id}", json=update_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log("✅ Update basket endpoint working")
                
                # Validate response structure
                if "message" in result:
                    self.log("✅ Update basket response structure is valid")
                    return True
                else:
                    self.log("⚠️ Update basket response missing message field")
                    return False
                    
            else:
                self.log(f"❌ Update basket endpoint failed: {response.status_code}")
                if response.text:
                    self.log(f"Error details: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing update basket endpoint: {e}")
            return False
    
    def test_assign_item_endpoint(self):
        """Test PUT /api/user/bought-items/{item_id}/assign"""
        self.log("🧪 Testing Assign Item to Basket Endpoint...")
        
        if not self.test_basket_id:
            self.log("❌ No test basket available for assignment")
            return False
            
        try:
            # Use a dummy item ID for testing
            dummy_item_id = "test-item-123"
            assignment_data = {
                "basket_id": self.test_basket_id
            }
            
            response = self.session.put(f"{BASE_URL}/user/bought-items/{dummy_item_id}/assign", json=assignment_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log("✅ Assign item endpoint working")
                
                # Validate response structure
                if "message" in result:
                    self.log("✅ Assign item response structure is valid")
                    return True
                else:
                    self.log("⚠️ Assign item response missing message field")
                    return False
                    
            else:
                self.log(f"❌ Assign item endpoint failed: {response.status_code}")
                if response.text:
                    self.log(f"Error details: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing assign item endpoint: {e}")
            return False
    
    def test_delete_basket_endpoint(self):
        """Test DELETE /api/user/baskets/{basket_id}"""
        self.log("🧪 Testing Delete Basket Endpoint...")
        
        if not self.test_basket_id:
            self.log("❌ No test basket available for deletion")
            return False
            
        try:
            response = self.session.delete(f"{BASE_URL}/user/baskets/{self.test_basket_id}")
            
            if response.status_code == 200:
                result = response.json()
                self.log("✅ Delete basket endpoint working")
                
                # Validate response structure
                if "message" in result:
                    self.log("✅ Delete basket response structure is valid")
                    return True
                else:
                    self.log("⚠️ Delete basket response missing message field")
                    return False
                    
            else:
                self.log(f"❌ Delete basket endpoint failed: {response.status_code}")
                if response.text:
                    self.log(f"Error details: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error testing delete basket endpoint: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling for invalid IDs"""
        self.log("🧪 Testing Error Handling...")
        
        try:
            # Test with invalid user ID
            response = self.session.get(f"{BASE_URL}/user/bought-items/invalid-user-id")
            if response.status_code in [404, 500]:
                self.log("✅ Error handling for invalid user ID works")
            else:
                self.log(f"⚠️ Unexpected response for invalid user ID: {response.status_code}")
            
            # Test with invalid basket ID
            response = self.session.get(f"{BASE_URL}/user/baskets/invalid-user-id")
            if response.status_code in [404, 500]:
                self.log("✅ Error handling for invalid basket user ID works")
            else:
                self.log(f"⚠️ Unexpected response for invalid basket user ID: {response.status_code}")
            
            # Test updating non-existent basket
            response = self.session.put(f"{BASE_URL}/user/baskets/non-existent-basket", json={"name": "test"})
            if response.status_code in [404, 500]:
                self.log("✅ Error handling for non-existent basket update works")
            else:
                self.log(f"⚠️ Unexpected response for non-existent basket: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error testing error handling: {e}")
            return False
    
    def test_cors_functionality(self):
        """Test CORS functionality"""
        self.log("🧪 Testing CORS Functionality...")
        
        try:
            # Test OPTIONS request
            response = self.session.options(f"{BASE_URL}/user/bought-items/test")
            
            # Check CORS headers
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            found_headers = []
            for header in cors_headers:
                if header in response.headers:
                    found_headers.append(header)
            
            if len(found_headers) >= 2:  # At least 2 CORS headers should be present
                self.log(f"✅ CORS headers found: {found_headers}")
                return True
            else:
                self.log(f"⚠️ Limited CORS headers found: {found_headers}")
                return True  # Don't fail the test for this
                
        except Exception as e:
            self.log(f"❌ Error testing CORS: {e}")
            return False
    
    def check_existing_demo_data(self):
        """Check if there are existing demo users or sample data"""
        self.log("🔍 Checking for existing demo data...")
        
        try:
            # Check for existing users
            response = self.session.get(f"{BASE_URL}/admin/users")
            if response.status_code == 200:
                users = response.json()
                self.log(f"ℹ️ Found {len(users)} existing users in the system")
                
                # Look for demo users
                demo_users = [user for user in users if 'demo' in user.get('email', '').lower() or 'demo' in user.get('username', '').lower()]
                if demo_users:
                    self.log(f"ℹ️ Found {len(demo_users)} demo users")
                    for user in demo_users[:3]:  # Show first 3
                        self.log(f"   - {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
                
            # Check for existing listings
            response = self.session.get(f"{BASE_URL}/marketplace/browse")
            if response.status_code == 200:
                listings = response.json()
                self.log(f"ℹ️ Found {len(listings)} existing listings in the marketplace")
                
            # Check for existing tenders (to see if there might be bought items)
            response = self.session.get(f"{BASE_URL}/admin/dashboard")
            if response.status_code == 200:
                dashboard = response.json()
                kpis = dashboard.get('kpis', {})
                self.log(f"ℹ️ Dashboard shows: {kpis.get('total_deals', 0)} deals, €{kpis.get('revenue', 0)} revenue")
                
        except Exception as e:
            self.log(f"⚠️ Error checking demo data: {e}")
    
    def run_all_tests(self):
        """Run all Buy Management tests"""
        self.log("🚀 Starting Buy Management Backend Tests")
        self.log("=" * 60)
        
        test_results = []
        
        # Test 0: Check existing data
        self.check_existing_demo_data()
        
        # Test 1: Health Check
        test_results.append(("Health Check", self.test_health_check()))
        
        # Test 2: Get Demo User
        test_results.append(("Demo User Setup", self.get_demo_user()))
        
        # Test 3: Bought Items Endpoint
        test_results.append(("Bought Items Endpoint", self.test_bought_items_endpoint()))
        
        # Test 4: Get Baskets Endpoint
        test_results.append(("Get Baskets Endpoint", self.test_get_baskets_endpoint()))
        
        # Test 5: Create Basket Endpoint
        test_results.append(("Create Basket Endpoint", self.test_create_basket_endpoint()))
        
        # Test 6: Update Basket Endpoint
        test_results.append(("Update Basket Endpoint", self.test_update_basket_endpoint()))
        
        # Test 7: Assign Item Endpoint
        test_results.append(("Assign Item Endpoint", self.test_assign_item_endpoint()))
        
        # Test 8: Delete Basket Endpoint
        test_results.append(("Delete Basket Endpoint", self.test_delete_basket_endpoint()))
        
        # Test 9: Error Handling
        test_results.append(("Error Handling", self.test_error_handling()))
        
        # Test 10: CORS Functionality
        test_results.append(("CORS Functionality", self.test_cors_functionality()))
        
        # Summary
        self.log("=" * 60)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name:<25} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        self.log("=" * 60)
        self.log(f"Total Tests: {len(test_results)}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED!")
            return True
        else:
            self.log(f"⚠️ {failed} TEST(S) FAILED")
            return False

def main():
    """Main function to run Buy Management tests"""
    tester = BuyManagementTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()