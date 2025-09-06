#!/usr/bin/env python3
"""
Cataloro Backend Testing Suite - Deep Basket Debug
Deep debugging of basket ID issues and assignment problems
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class BasketDebugTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.demo_user = None
        
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

    def setup_demo_user(self):
        """Login as demo user to get user context"""
        try:
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
                self.demo_user = data.get('user', {})
                self.log_test(
                    "Demo User Login Setup", 
                    True, 
                    f"Logged in as demo user: {self.demo_user.get('username', 'Unknown')} (ID: {self.demo_user.get('id')})"
                )
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Demo User Login Setup", False, error_msg=error_detail)
                return False
        except Exception as e:
            self.log_test("Demo User Login Setup", False, error_msg=str(e))
            return False

    def analyze_all_baskets(self):
        """Analyze all baskets in detail"""
        if not self.demo_user:
            self.log_test("Analyze All Baskets", False, error_msg="No demo user available")
            return []
            
        try:
            user_id = self.demo_user.get('id')
            
            response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
            
            if response.status_code == 200:
                baskets = response.json()
                
                basket_analysis = []
                for i, basket in enumerate(baskets):
                    analysis = {
                        "index": i,
                        "name": basket.get('name', 'Unnamed'),
                        "id": basket.get('id', 'No ID'),
                        "user_id": basket.get('user_id', 'No User ID'),
                        "id_format": "Unknown",
                        "id_length": len(basket.get('id', '')),
                        "has_hyphens": '-' in basket.get('id', ''),
                        "created_at": basket.get('created_at', 'Unknown')
                    }
                    
                    # Check ID format
                    basket_id = basket.get('id', '')
                    try:
                        uuid.UUID(basket_id)
                        analysis["id_format"] = "Valid UUID"
                    except ValueError:
                        if len(basket_id) == 24 and all(c in '0123456789abcdef' for c in basket_id):
                            analysis["id_format"] = "MongoDB ObjectId"
                        else:
                            analysis["id_format"] = "Unknown format"
                    
                    basket_analysis.append(analysis)
                
                # Create detailed report
                details_lines = []
                for analysis in basket_analysis:
                    details_lines.append(
                        f"Basket {analysis['index']}: '{analysis['name']}' | "
                        f"ID: {analysis['id']} | "
                        f"Format: {analysis['id_format']} | "
                        f"Length: {analysis['id_length']} | "
                        f"Hyphens: {analysis['has_hyphens']}"
                    )
                
                self.log_test(
                    "Analyze All Baskets", 
                    True, 
                    f"Found {len(baskets)} baskets:\n" + "\n".join(details_lines)
                )
                return basket_analysis
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                self.log_test("Analyze All Baskets", False, error_msg=f"Failed to get baskets: {error_detail}")
                return []
                
        except Exception as e:
            self.log_test("Analyze All Baskets", False, error_msg=str(e))
            return []

    def test_assignment_with_each_basket_id(self, basket_analysis):
        """Test assignment with each basket ID to see which ones work"""
        if not basket_analysis:
            self.log_test("Test Assignment with Each Basket ID", False, error_msg="No basket analysis available")
            return False
            
        try:
            # Use a test item ID (we'll use one of the existing bought items)
            user_id = self.demo_user.get('id')
            bought_items_response = requests.get(f"{BACKEND_URL}/user/bought-items/{user_id}", timeout=10)
            
            if bought_items_response.status_code != 200:
                self.log_test("Test Assignment with Each Basket ID", False, error_msg="Failed to get bought items for testing")
                return False
            
            bought_items = bought_items_response.json()
            if not bought_items:
                self.log_test("Test Assignment with Each Basket ID", False, error_msg="No bought items available for testing")
                return False
            
            test_item_id = bought_items[0].get('id')
            test_results = []
            
            for analysis in basket_analysis:
                basket_name = analysis['name']
                basket_id = analysis['id']
                
                try:
                    assignment_data = {"basket_id": basket_id}
                    
                    response = requests.put(
                        f"{BACKEND_URL}/user/bought-items/{test_item_id}/assign",
                        json=assignment_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        test_results.append(f"'{basket_name}' (ID: {basket_id}): ✅ SUCCESS")
                    else:
                        error_detail = response.json().get('detail', 'Unknown error') if response.content else f"HTTP {response.status_code}"
                        test_results.append(f"'{basket_name}' (ID: {basket_id}): ❌ {error_detail}")
                        
                except Exception as e:
                    test_results.append(f"'{basket_name}' (ID: {basket_id}): ❌ Exception: {str(e)}")
            
            success = any("✅ SUCCESS" in result for result in test_results)
            
            self.log_test(
                "Test Assignment with Each Basket ID", 
                success, 
                f"Assignment test results:\n" + "\n".join(test_results)
            )
            return success
            
        except Exception as e:
            self.log_test("Test Assignment with Each Basket ID", False, error_msg=str(e))
            return False

    def check_database_consistency(self, basket_analysis):
        """Check if there are database consistency issues"""
        if not basket_analysis:
            self.log_test("Check Database Consistency", False, error_msg="No basket analysis available")
            return False
            
        try:
            consistency_issues = []
            
            # Check for duplicate names
            names = [b['name'] for b in basket_analysis]
            duplicate_names = [name for name in set(names) if names.count(name) > 1]
            if duplicate_names:
                consistency_issues.append(f"Duplicate basket names: {duplicate_names}")
            
            # Check for ID format inconsistencies
            id_formats = [b['id_format'] for b in basket_analysis]
            unique_formats = set(id_formats)
            if len(unique_formats) > 1:
                consistency_issues.append(f"Mixed ID formats: {unique_formats}")
            
            # Check for user_id consistency
            user_ids = [b['user_id'] for b in basket_analysis]
            unique_user_ids = set(user_ids)
            if len(unique_user_ids) > 1:
                consistency_issues.append(f"Multiple user IDs: {unique_user_ids}")
            
            # Check for empty/invalid IDs
            invalid_ids = [b for b in basket_analysis if not b['id'] or b['id'] == 'No ID']
            if invalid_ids:
                consistency_issues.append(f"Baskets with invalid IDs: {[b['name'] for b in invalid_ids]}")
            
            if consistency_issues:
                self.log_test(
                    "Check Database Consistency", 
                    False, 
                    f"Found consistency issues: {'; '.join(consistency_issues)}"
                )
            else:
                self.log_test(
                    "Check Database Consistency", 
                    True, 
                    "No database consistency issues found"
                )
            
            return len(consistency_issues) == 0
            
        except Exception as e:
            self.log_test("Check Database Consistency", False, error_msg=str(e))
            return False

    def test_direct_basket_lookup(self, basket_analysis):
        """Test direct basket lookup to see what the backend finds"""
        if not basket_analysis:
            self.log_test("Test Direct Basket Lookup", False, error_msg="No basket analysis available")
            return False
            
        try:
            # Find picki baskets
            picki_baskets = [b for b in basket_analysis if 'picki' in b['name'].lower()]
            
            if not picki_baskets:
                self.log_test("Test Direct Basket Lookup", False, error_msg="No picki baskets found")
                return False
            
            lookup_results = []
            
            for picki_basket in picki_baskets:
                basket_id = picki_basket['id']
                basket_name = picki_basket['name']
                
                # Simulate what the backend does - look up basket by ID
                user_id = self.demo_user.get('id')
                response = requests.get(f"{BACKEND_URL}/user/baskets/{user_id}", timeout=10)
                
                if response.status_code == 200:
                    all_baskets = response.json()
                    found_basket = None
                    
                    for basket in all_baskets:
                        if basket.get('id') == basket_id:
                            found_basket = basket
                            break
                    
                    if found_basket:
                        lookup_results.append(f"'{basket_name}' (ID: {basket_id}): ✅ Found in database")
                    else:
                        lookup_results.append(f"'{basket_name}' (ID: {basket_id}): ❌ NOT found in database")
                else:
                    lookup_results.append(f"'{basket_name}' (ID: {basket_id}): ❌ Error getting baskets")
            
            success = any("✅ Found" in result for result in lookup_results)
            
            self.log_test(
                "Test Direct Basket Lookup", 
                success, 
                f"Direct lookup results:\n" + "\n".join(lookup_results)
            )
            return success
            
        except Exception as e:
            self.log_test("Test Direct Basket Lookup", False, error_msg=str(e))
            return False

    def run_basket_debug_test(self):
        """Run the complete basket debug test"""
        print("=" * 80)
        print("CATALORO DEEP BASKET DEBUG TEST")
        print("Deep debugging of basket ID issues and assignment problems")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Started: {datetime.now().isoformat()}")
        print()
        
        # 1. Setup demo user
        print("👤 SETUP DEMO USER")
        print("-" * 40)
        if not self.setup_demo_user():
            print("❌ Failed to setup demo user. Aborting test.")
            return
        
        # 2. Analyze all baskets
        print("🔍 ANALYZE ALL BASKETS")
        print("-" * 40)
        basket_analysis = self.analyze_all_baskets()
        
        # 3. Check database consistency
        print("🔧 CHECK DATABASE CONSISTENCY")
        print("-" * 40)
        self.check_database_consistency(basket_analysis)
        
        # 4. Test direct basket lookup
        print("🎯 TEST DIRECT BASKET LOOKUP")
        print("-" * 40)
        self.test_direct_basket_lookup(basket_analysis)
        
        # 5. Test assignment with each basket ID
        print("📝 TEST ASSIGNMENT WITH EACH BASKET ID")
        print("-" * 40)
        self.test_assignment_with_each_basket_id(basket_analysis)
        
        # Print Summary
        print("=" * 80)
        print("DEEP BASKET DEBUG TEST SUMMARY")
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
        
        print("\n🎯 DEEP BASKET DEBUG TEST COMPLETE")
        
        return self.passed_tests, self.failed_tests, self.test_results

if __name__ == "__main__":
    tester = BasketDebugTester()
    
    print("🎯 RUNNING DEEP BASKET DEBUG TEST")
    print("Deep debugging of basket ID issues and assignment problems...")
    print()
    
    passed, failed, results = tester.run_basket_debug_test()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)