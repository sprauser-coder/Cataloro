#!/usr/bin/env python3
"""
Seller Name Debug Test - Cataloro Backend Testing
Debug why seller name is showing as "Unknown" in bought items
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://market-evolution-2.preview.emergentagent.com/api"

class SellerNameDebugTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, success, details="", error_msg=""):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error_msg,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error_msg:
            print(f"   Error: {error_msg}")
        print()

    def test_health_check(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Status: {data.get('status')}, App: {data.get('app')}, Version: {data.get('version')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def get_demo_user(self):
        """Get demo user for testing"""
        try:
            # Login as demo user
            demo_credentials = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/auth/login", 
                json=demo_credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                return user
            else:
                print(f"Failed to login demo user: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting demo user: {e}")
            return None

    def test_bought_items_endpoint(self, user_id):
        """Test GET /api/user/bought-items/{user_id} endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if response.status_code == 200:
                bought_items = response.json()
                
                if isinstance(bought_items, list):
                    item_count = len(bought_items)
                    
                    # Analyze seller data in each item
                    seller_analysis = []
                    unknown_sellers = 0
                    valid_sellers = 0
                    
                    for i, item in enumerate(bought_items):
                        seller_name = item.get('seller_name', 'Not Set')
                        seller_id = item.get('seller_id', 'Not Set')
                        listing_id = item.get('listing_id', 'Not Set')
                        title = item.get('title', 'Unknown')
                        
                        if seller_name == "Unknown":
                            unknown_sellers += 1
                            seller_analysis.append(f"Item {i+1} ({title[:30]}...): seller_name='{seller_name}', seller_id='{seller_id}', listing_id='{listing_id}'")
                        else:
                            valid_sellers += 1
                            seller_analysis.append(f"Item {i+1} ({title[:30]}...): seller_name='{seller_name}', seller_id='{seller_id}'")
                    
                    details = f"Found {item_count} bought items. Unknown sellers: {unknown_sellers}, Valid sellers: {valid_sellers}"
                    if seller_analysis:
                        details += f"\nSeller Analysis:\n" + "\n".join(seller_analysis[:5])  # Show first 5 items
                    
                    self.log_test(
                        "GET /api/user/bought-items/{user_id} Endpoint Test", 
                        True, 
                        details
                    )
                    return bought_items
                else:
                    self.log_test(
                        "GET /api/user/bought-items/{user_id} Endpoint Test", 
                        False, 
                        f"Expected list, got {type(bought_items)}: {bought_items}"
                    )
                    return []
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test(
                    "GET /api/user/bought-items/{user_id} Endpoint Test", 
                    False, 
                    error_msg=error_detail
                )
                return []
        except Exception as e:
            self.log_test(
                "GET /api/user/bought-items/{user_id} Endpoint Test", 
                False, 
                error_msg=str(e)
            )
            return []

    def test_seller_user_records(self, bought_items):
        """Check if seller_id in items has valid user records"""
        try:
            if not bought_items:
                self.log_test(
                    "Seller User Records Validation", 
                    False, 
                    "No bought items to check"
                )
                return
            
            # Get unique seller IDs from bought items
            seller_ids = set()
            for item in bought_items:
                seller_id = item.get('seller_id')
                if seller_id and seller_id != 'Not Set':
                    seller_ids.add(seller_id)
            
            if not seller_ids:
                self.log_test(
                    "Seller User Records Validation", 
                    False, 
                    "No seller IDs found in bought items"
                )
                return
            
            # Check each seller ID in users collection
            seller_validation_results = []
            valid_sellers = 0
            invalid_sellers = 0
            
            for seller_id in list(seller_ids)[:5]:  # Check first 5 sellers
                try:
                    # Try to get seller profile
                    response = requests.get(f"{BACKEND_URL}/auth/profile/{seller_id}", timeout=10)
                    
                    if response.status_code == 200:
                        seller_data = response.json()
                        username = seller_data.get('username', 'No Username')
                        email = seller_data.get('email', 'No Email')
                        full_name = seller_data.get('full_name', 'No Full Name')
                        
                        valid_sellers += 1
                        seller_validation_results.append(
                            f"Seller {seller_id[:8]}...: ✅ FOUND - username='{username}', email='{email}', full_name='{full_name}'"
                        )
                    else:
                        invalid_sellers += 1
                        seller_validation_results.append(
                            f"Seller {seller_id[:8]}...: ❌ NOT FOUND - HTTP {response.status_code}"
                        )
                except Exception as e:
                    invalid_sellers += 1
                    seller_validation_results.append(
                        f"Seller {seller_id[:8]}...: ❌ ERROR - {str(e)}"
                    )
            
            details = f"Checked {len(seller_ids)} unique seller IDs. Valid: {valid_sellers}, Invalid: {invalid_sellers}"
            details += f"\nSeller Validation Results:\n" + "\n".join(seller_validation_results)
            
            success = invalid_sellers == 0
            self.log_test(
                "Seller User Records Validation", 
                success, 
                details
            )
            
        except Exception as e:
            self.log_test(
                "Seller User Records Validation", 
                False, 
                error_msg=str(e)
            )

    def test_users_collection_username_data(self):
        """Test if users collection has valid username data"""
        try:
            # Get all users to check username field population
            response = requests.get(f"{BACKEND_URL}/admin/users", timeout=10)
            
            if response.status_code == 200:
                users = response.json()
                
                if isinstance(users, list):
                    total_users = len(users)
                    users_with_username = 0
                    users_without_username = 0
                    username_analysis = []
                    
                    for i, user in enumerate(users[:10]):  # Check first 10 users
                        user_id = user.get('id', 'No ID')
                        username = user.get('username', None)
                        email = user.get('email', 'No Email')
                        full_name = user.get('full_name', 'No Full Name')
                        
                        if username and username.strip():
                            users_with_username += 1
                            username_analysis.append(
                                f"User {i+1} ({user_id[:8]}...): ✅ username='{username}', email='{email}'"
                            )
                        else:
                            users_without_username += 1
                            username_analysis.append(
                                f"User {i+1} ({user_id[:8]}...): ❌ NO USERNAME, email='{email}', full_name='{full_name}'"
                            )
                    
                    details = f"Total users: {total_users}. With username: {users_with_username}, Without username: {users_without_username}"
                    details += f"\nUsername Analysis (first 10 users):\n" + "\n".join(username_analysis)
                    
                    success = users_without_username == 0
                    self.log_test(
                        "Users Collection Username Data Test", 
                        success, 
                        details
                    )
                else:
                    self.log_test(
                        "Users Collection Username Data Test", 
                        False, 
                        f"Expected list, got {type(users)}: {users}"
                    )
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test(
                    "Users Collection Username Data Test", 
                    False, 
                    error_msg=error_detail
                )
                
        except Exception as e:
            self.log_test(
                "Users Collection Username Data Test", 
                False, 
                error_msg=str(e)
            )

    def test_seller_data_examples(self, bought_items):
        """Provide examples of seller data returned vs expected"""
        try:
            if not bought_items:
                self.log_test(
                    "Seller Data Examples Analysis", 
                    False, 
                    "No bought items to analyze"
                )
                return
            
            examples = []
            
            for i, item in enumerate(bought_items[:3]):  # Analyze first 3 items
                seller_name = item.get('seller_name', 'Not Set')
                seller_id = item.get('seller_id', 'Not Set')
                listing_id = item.get('listing_id', 'Not Set')
                title = item.get('title', 'Unknown')
                
                # Try to get actual seller data
                actual_seller_data = "Could not fetch"
                if seller_id and seller_id != 'Not Set':
                    try:
                        response = requests.get(f"{BACKEND_URL}/auth/profile/{seller_id}", timeout=10)
                        if response.status_code == 200:
                            seller_profile = response.json()
                            actual_seller_data = {
                                "username": seller_profile.get('username', 'No Username'),
                                "email": seller_profile.get('email', 'No Email'),
                                "full_name": seller_profile.get('full_name', 'No Full Name')
                            }
                    except Exception as e:
                        actual_seller_data = f"Error: {str(e)}"
                
                example = f"""
Example {i+1} - Item: {title[:40]}...
  Listing ID: {listing_id}
  Seller ID: {seller_id}
  RETURNED seller_name: '{seller_name}'
  ACTUAL seller data: {actual_seller_data}
  EXPECTED: Should show username from seller profile if exists
"""
                examples.append(example)
            
            details = "Seller Data Analysis Examples:" + "".join(examples)
            
            # Check if any items have "Unknown" seller names
            unknown_count = sum(1 for item in bought_items if item.get('seller_name') == 'Unknown')
            success = unknown_count == 0
            
            self.log_test(
                "Seller Data Examples Analysis", 
                success, 
                details
            )
            
        except Exception as e:
            self.log_test(
                "Seller Data Examples Analysis", 
                False, 
                error_msg=str(e)
            )

    def run_seller_name_debug_testing(self):
        """Run seller name debug testing as requested in review"""
        print("=" * 80)
        print("SELLER NAME DEBUG TESTING - CATALORO BACKEND")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        print("🎯 DEBUGGING: Why seller name is showing as 'Unknown' in bought items")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting seller name debug testing.")
            return
        
        # 2. Get Demo User
        print("👤 GET DEMO USER FOR TESTING")
        print("-" * 40)
        demo_user = self.get_demo_user()
        if not demo_user:
            print("❌ Failed to get demo user. Aborting tests.")
            return
        
        user_id = demo_user.get('id')
        print(f"✅ Using demo user ID: {user_id}")
        print()
        
        # 3. Test GET /api/user/bought-items/{user_id} endpoint
        print("🛒 TEST GET /api/user/bought-items/{user_id} ENDPOINT")
        print("-" * 40)
        bought_items = self.test_bought_items_endpoint(user_id)
        
        # 4. Check seller_id validity in user records
        print("👥 CHECK SELLER USER RECORDS VALIDITY")
        print("-" * 40)
        self.test_seller_user_records(bought_items)
        
        # 5. Test users collection username data
        print("📊 TEST USERS COLLECTION USERNAME DATA")
        print("-" * 40)
        self.test_users_collection_username_data()
        
        # 6. Provide seller data examples
        print("📋 SELLER DATA EXAMPLES ANALYSIS")
        print("-" * 40)
        self.test_seller_data_examples(bought_items)
        
        # Print Summary
        print("=" * 80)
        print("SELLER NAME DEBUG TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 SELLER NAME DEBUG TESTING COMPLETE")
        print("Expected Findings:")
        print("  1. GET /api/user/bought-items/{user_id} should return seller data")
        print("  2. seller_id in items should have valid user records")
        print("  3. Users collection should have username data populated")
        print("  4. Examples should show actual vs expected seller data")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = SellerNameDebugTester()
    
    # Run seller name debug testing as requested in the review
    print("🎯 RUNNING SELLER NAME DEBUG TESTING AS REQUESTED")
    print("Investigating why seller name shows as 'Unknown' in bought items...")
    print()
    
    passed, failed, results = tester.run_seller_name_debug_testing()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)