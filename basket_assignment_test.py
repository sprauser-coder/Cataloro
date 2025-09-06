#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Basket Delete & Assignment Testing
Testing fixed basket delete functionality and assignment process as requested in review
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class BasketAssignmentTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.created_data = {
            "listings": [],
            "tenders": [],
            "baskets": [],
            "bought_items": []
        }
        
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
                    f"Status: {data.get('status')}, App: {data.get('app')}"
                )
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error_msg=str(e))
            return False

    def get_admin_user_id(self):
        """Get admin user ID for creating listings"""
        try:
            # Login as admin to get user ID
            login_data = {
                "email": "admin@cataloro.com",
                "password": "admin123"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                admin_id = user.get('id')
                self.log_test(
                    "Get Admin User ID", 
                    True, 
                    f"Admin ID: {admin_id}, Role: {user.get('user_role')}"
                )
                return admin_id
            else:
                self.log_test("Get Admin User ID", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Admin User ID", False, error_msg=str(e))
            return None

    def get_demo_user_id(self):
        """Get demo user ID for creating tenders"""
        try:
            # Login as demo user to get user ID
            login_data = {
                "email": "demo@cataloro.com",
                "password": "demo123"
            }
            
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                demo_id = user.get('id')
                self.log_test(
                    "Get Demo User ID", 
                    True, 
                    f"Demo ID: {demo_id}, Role: {user.get('user_role')}"
                )
                return demo_id
            else:
                self.log_test("Get Demo User ID", False, f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Demo User ID", False, error_msg=str(e))
            return None

    def create_test_listing(self, admin_id):
        """Create a new listing from admin user"""
        try:
            listing_data = {
                "title": f"Test Assignment Item {str(uuid.uuid4())[:8]}",
                "description": "Test item for assignment functionality testing",
                "price": 199.99,
                "category": "Electronics",
                "condition": "New",
                "seller_id": admin_id,
                "status": "active",
                "images": ["https://example.com/test-item.jpg"],
                "tags": ["test", "assignment", "electronics"]
            }
            
            response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                listing_id = data.get('listing_id') or data.get('id')
                self.created_data["listings"].append(listing_id)
                self.log_test(
                    "Create Test Listing", 
                    True, 
                    f"Created listing: {listing_data['title']} (ID: {listing_id})"
                )
                return listing_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Listing", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test Listing", False, error_msg=str(e))
            return None

    def create_test_tender(self, demo_id, listing_id):
        """Create a tender from demo user for the listing"""
        try:
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": demo_id,
                "offer_amount": 175.00,
                "message": "Test tender for assignment functionality",
                "status": "pending"
            }
            
            response = requests.post(f"{BACKEND_URL}/tenders", json=tender_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tender_id = data.get('tender_id') or data.get('id')
                self.created_data["tenders"].append(tender_id)
                self.log_test(
                    "Create Test Tender", 
                    True, 
                    f"Created tender: €{tender_data['offer_amount']} for listing {listing_id} (ID: {tender_id})"
                )
                return tender_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Tender", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test Tender", False, error_msg=str(e))
            return None

    def accept_tender(self, tender_id):
        """Accept the tender to create a bought item"""
        try:
            response = requests.put(f"{BACKEND_URL}/tenders/{tender_id}/accept", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Accept Tender", 
                    True, 
                    f"Successfully accepted tender {tender_id}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Accept Tender", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Accept Tender", False, error_msg=str(e))
            return False

    def get_bought_items(self, user_id):
        """Get bought items for a user"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            if response.status_code == 200:
                items = response.json()
                item_count = len(items) if isinstance(items, list) else 0
                unassigned_count = len([item for item in items if not item.get('basket_id')])
                self.log_test(
                    "Get Bought Items", 
                    True, 
                    f"Retrieved {item_count} bought items, {unassigned_count} unassigned"
                )
                return items
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Get Bought Items", False, error_msg=error_detail)
                return []
        except Exception as e:
            self.log_test("Get Bought Items", False, error_msg=str(e))
            return []

    def create_test_basket(self, user_id):
        """Create a test basket for assignment testing"""
        try:
            basket_data = {
                "name": f"Test Assignment Basket {str(uuid.uuid4())[:8]}",
                "description": "Test basket for assignment functionality testing",
                "user_id": user_id
            }
            
            response = requests.post(f"{BACKEND_URL}/user/baskets", json=basket_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                basket_id = data.get('basket_id') or data.get('id')
                self.created_data["baskets"].append(basket_id)
                self.log_test(
                    "Create Test Basket", 
                    True, 
                    f"Created basket: {basket_data['name']} (ID: {basket_id})"
                )
                return basket_id
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Create Test Basket", False, error_msg=error_detail)
                return None
        except Exception as e:
            self.log_test("Create Test Basket", False, error_msg=str(e))
            return None

    def test_assignment_endpoint(self, user_id, item_id, basket_id):
        """Test the assignment endpoint with unassigned item"""
        try:
            assignment_data = {
                "item_ids": [item_id],
                "basket_id": basket_id
            }
            
            response = requests.post(f"{BACKEND_URL}/user/assign-items", json=assignment_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Test Assignment Endpoint", 
                    True, 
                    f"Successfully assigned item {item_id} to basket {basket_id}"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Test Assignment Endpoint", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Test Assignment Endpoint", False, error_msg=str(e))
            return False

    def get_user_baskets(self, user_id):
        """Get user baskets to verify assignment"""
        try:
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            if response.status_code == 200:
                baskets = response.json()
                basket_count = len(baskets) if isinstance(baskets, list) else 0
                self.log_test(
                    "Get User Baskets", 
                    True, 
                    f"Retrieved {basket_count} baskets for user {user_id}"
                )
                return baskets
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Get User Baskets", False, error_msg=error_detail)
                return []
        except Exception as e:
            self.log_test("Get User Baskets", False, error_msg=str(e))
            return []

    def test_delete_basket_endpoint(self, basket_id):
        """Test the fixed DELETE basket endpoint with improved logging"""
        try:
            print(f"🗑️  Testing DELETE /api/user/baskets/{basket_id}")
            
            response = requests.delete(f"{BACKEND_URL}/user/baskets/{basket_id}", timeout=10)
            
            # Log detailed response information
            print(f"   Response Status: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            
            if response.content:
                try:
                    response_data = response.json()
                    print(f"   Response Body: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"   Response Body (raw): {response.text}")
            else:
                print("   Response Body: Empty")
            
            if response.status_code == 200:
                data = response.json() if response.content else {}
                self.log_test(
                    "Test Fixed Delete Basket Endpoint", 
                    True, 
                    f"Successfully deleted basket {basket_id}. Response: {data.get('message', 'No message')}"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Test Fixed Delete Basket Endpoint", 
                    False, 
                    f"Basket {basket_id} not found (404). May have been already deleted or doesn't exist."
                )
                return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Test Fixed Delete Basket Endpoint", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Test Fixed Delete Basket Endpoint", False, error_msg=str(e))
            return False

    def verify_complete_workflow(self, demo_id):
        """Verify the complete assignment workflow"""
        try:
            # Check bought items API
            bought_items = self.get_bought_items(demo_id)
            
            # Check baskets API
            baskets = self.get_user_baskets(demo_id)
            
            # Verify assignment functionality
            assigned_items = [item for item in bought_items if item.get('basket_id')]
            unassigned_items = [item for item in bought_items if not item.get('basket_id')]
            
            workflow_success = True
            workflow_details = []
            
            # Check if we have both assigned and unassigned items
            if len(assigned_items) > 0:
                workflow_details.append(f"✅ {len(assigned_items)} assigned items found")
            else:
                workflow_details.append("⚠️  No assigned items found")
            
            if len(unassigned_items) > 0:
                workflow_details.append(f"✅ {len(unassigned_items)} unassigned items available for testing")
            else:
                workflow_details.append("⚠️  No unassigned items found")
            
            if len(baskets) > 0:
                workflow_details.append(f"✅ {len(baskets)} baskets available")
            else:
                workflow_details.append("⚠️  No baskets found")
                workflow_success = False
            
            self.log_test(
                "Verify Complete Workflow", 
                workflow_success, 
                f"Workflow verification: {'; '.join(workflow_details)}"
            )
            return workflow_success, bought_items, baskets
            
        except Exception as e:
            self.log_test("Verify Complete Workflow", False, error_msg=str(e))
            return False, [], []

    def run_comprehensive_basket_assignment_tests(self):
        """Run comprehensive basket delete and assignment testing"""
        print("=" * 80)
        print("CATALORO BASKET DELETE & ASSIGNMENT TESTING")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Basic Health Check
        print("🔍 BASIC HEALTH CHECK")
        print("-" * 40)
        if not self.test_health_check():
            print("❌ Health check failed. Aborting tests.")
            return 0, 1, []
        
        # 2. Get User IDs
        print("👤 GET USER IDS")
        print("-" * 40)
        admin_id = self.get_admin_user_id()
        demo_id = self.get_demo_user_id()
        
        if not admin_id or not demo_id:
            print("❌ Failed to get required user IDs. Aborting tests.")
            return 0, 1, []
        
        # 3. Create Additional Test Data
        print("📦 CREATE ADDITIONAL TEST DATA")
        print("-" * 40)
        
        # Create new listing from admin user
        listing_id = self.create_test_listing(admin_id)
        if not listing_id:
            print("❌ Failed to create test listing. Aborting tests.")
            return 0, 1, []
        
        # Create tender from demo user
        tender_id = self.create_test_tender(demo_id, listing_id)
        if not tender_id:
            print("❌ Failed to create test tender. Aborting tests.")
            return
        
        # Accept tender to create bought item
        if not self.accept_tender(tender_id):
            print("❌ Failed to accept tender. Aborting tests.")
            return
        
        # Wait a moment for data to be processed
        time.sleep(2)
        
        # 4. Test Assignment Process
        print("🔄 TEST ASSIGNMENT PROCESS")
        print("-" * 40)
        
        # Get bought items to find unassigned item
        bought_items = self.get_bought_items(demo_id)
        unassigned_items = [item for item in bought_items if not item.get('basket_id')]
        
        if not unassigned_items:
            print("⚠️  No unassigned items found. Creating a basket anyway for delete testing.")
        else:
            print(f"✅ Found {len(unassigned_items)} unassigned items for testing")
        
        # Create test basket
        basket_id = self.create_test_basket(demo_id)
        if not basket_id:
            print("❌ Failed to create test basket. Aborting assignment tests.")
            return
        
        # Test assignment if we have unassigned items
        if unassigned_items:
            item_id = unassigned_items[0].get('id')
            if item_id:
                self.test_assignment_endpoint(demo_id, item_id, basket_id)
        
        # 5. Test Fixed Delete Basket Endpoint
        print("🗑️  TEST FIXED DELETE BASKET ENDPOINT")
        print("-" * 40)
        
        # Test delete with the basket we created
        self.test_delete_basket_endpoint(basket_id)
        
        # 6. Verify Complete Workflow
        print("✅ VERIFY COMPLETE WORKFLOW")
        print("-" * 40)
        
        workflow_success, final_bought_items, final_baskets = self.verify_complete_workflow(demo_id)
        
        # Print Summary
        print("=" * 80)
        print("BASKET DELETE & ASSIGNMENT TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print()
        
        # Print created data summary
        print("CREATED TEST DATA:")
        print(f"  Listings: {len(self.created_data['listings'])}")
        print(f"  Tenders: {len(self.created_data['tenders'])}")
        print(f"  Baskets: {len(self.created_data['baskets'])}")
        print()
        
        if self.failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        print("\n🎯 BASKET DELETE & ASSIGNMENT TESTING COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketAssignmentTester()
    
    print("🎯 RUNNING BASKET DELETE & ASSIGNMENT TESTING AS REQUESTED")
    print("Testing fixed delete basket functionality and assignment process...")
    print()
    
    passed, failed, results = tester.run_comprehensive_basket_assignment_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)